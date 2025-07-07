import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

import streamlit as st
import yaml
from streamlit_authenticator import Hasher

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

if not os.path.exists("painel_admin/logs"):
    os.makedirs("painel_admin/logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(username)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("painel_admin/logs/sistema.log"),
        logging.StreamHandler()
    ]
)

if not st.session_state.get("logged_in"):
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

def aplicar_tema(tema: str):
    if tema == "Escuro":
        st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        .stSelectbox > div > div {
            background-color: #262730;
            color: #ffffff;
        }
        .stTextInput > div > div > input {
            background-color: #262730;
            color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)
    elif tema == "Claro":
        st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        </style>
        """, unsafe_allow_html=True)

def carregar_configuracoes() -> Dict[str, Any]:
    config_file = "painel_admin/configuracoes.json"
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "tema": "Auto",
        "idioma": "Português",
        "timeout_sessao": 30,
        "notificacoes_email": False,
        "email_smtp": {
            "servidor": "",
            "porta": 587,
            "usuario": "",
            "senha": "",
            "ssl": True
        }
    }

def salvar_configuracoes(config: Dict[str, Any]):
    config_file = "painel_admin/configuracoes.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def log_atividade(acao: str, detalhes: str = ""):
    logger = logging.getLogger(__name__)
    username = st.session_state.get("username", "desconhecido")
    
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.username = username
        return record
    logging.setLogRecordFactory(record_factory)
    
    logger.info(f"{acao} - {detalhes}")

def verificar_timeout_sessao():
    if "login_time" not in st.session_state:
        return False
    
    config = carregar_configuracoes()
    timeout_minutos = config.get("timeout_sessao", 30)
    
    login_time = st.session_state.get("login_time")
    if isinstance(login_time, str):
        login_time = datetime.fromisoformat(login_time)
    
    tempo_limite = login_time + timedelta(minutes=timeout_minutos)
    
    if datetime.now() > tempo_limite:
        st.session_state.clear()
        st.error("Sessão expirada. Faça login novamente.")
        st.rerun()
    
    return True

def resetar_configuracoes():
    config_padrao = {
        "tema": "Auto",
        "idioma": "Português",
        "timeout_sessao": 30,
        "notificacoes_email": False,
        "email_smtp": {
            "servidor": "",
            "porta": 587,
            "usuario": "",
            "senha": "",
            "ssl": True
        }
    }
    salvar_configuracoes(config_padrao)
    log_atividade("Configurações resetadas", "Todas as configurações foram restauradas para padrão")

def verificar_senha_atual(senha_atual: str, username: str) -> bool:
    dados_usuarios = carregar_usuarios()
    if username not in dados_usuarios.get("usernames", {}):
        return False
    
    senha_hash = dados_usuarios["usernames"][username]["password"]
    hasher = Hasher([senha_atual])
    return hasher.check([senha_hash], [senha_atual])[0]

def obter_logs_sistema(limite: int = 50) -> list:
    log_file = "painel_admin/logs/sistema.log"
    if not os.path.exists(log_file):
        return []
    
    logs = []
    with open(log_file, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        for linha in linhas[-limite:]:
            logs.append(linha.strip())
    
    return logs

verificar_timeout_sessao()

config = carregar_configuracoes()

aplicar_tema(config.get("tema", "Auto"))

st.set_page_config(page_title="Ajustes", page_icon="⚙️", layout="wide")

ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"

@st.cache_data
def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, "w") as f:
        yaml.dump(dados, f, default_flow_style=False)

st.title("⚙️ Configurações e Ajustes")

dados_usuarios = carregar_usuarios()
usuario_atual = st.session_state.get("username")

if usuario_atual and usuario_atual in dados_usuarios.get("usernames", {}):
    user_data = dados_usuarios["usernames"][usuario_atual]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Informações Pessoais")
        novo_nome = st.text_input("Nome completo", value=user_data.get("name", ""))
        novo_email = st.text_input("Email", value=user_data.get("email", ""))
        
        if st.button("💾 Salvar Alterações"):
            if novo_nome and novo_email:
                dados_usuarios["usernames"][usuario_atual]["name"] = novo_nome
                dados_usuarios["usernames"][usuario_atual]["email"] = novo_email
                salvar_usuarios(dados_usuarios)
                log_atividade("Informações atualizadas", f"Nome: {novo_nome}, Email: {novo_email}")
                st.success("Informações atualizadas com sucesso!")
                st.rerun()
            else:
                st.warning("Preencha todos os campos.")
    
    with col2:
        st.subheader("Alterar Senha")
        senha_atual = st.text_input("Senha atual", type="password")
        nova_senha = st.text_input("Nova senha", type="password")
        confirmar_senha = st.text_input("Confirmar nova senha", type="password")
        
        if st.button("🔒 Alterar Senha"):
            if not senha_atual or not nova_senha or not confirmar_senha:
                st.warning("Preencha todos os campos.")
            elif not verificar_senha_atual(senha_atual, usuario_atual):
                st.error("Senha atual incorreta.")
            elif nova_senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            elif len(nova_senha) < 4:
                st.error("A senha deve ter pelo menos 4 caracteres.")
            else:
                nova_senha_hash = Hasher([nova_senha]).generate()[0]
                dados_usuarios["usernames"][usuario_atual]["password"] = nova_senha_hash
                salvar_usuarios(dados_usuarios)
                log_atividade("Senha alterada", "Senha do usuário foi alterada com sucesso")
                st.success("Senha alterada com sucesso!")

st.divider()
st.subheader("Configurações do Sistema")

col1, col2 = st.columns(2)
with col1:
    tema_atual = st.selectbox(
        "Tema", 
        ["Claro", "Escuro", "Auto"], 
        index=["Claro", "Escuro", "Auto"].index(config.get("tema", "Auto")),
        help="Configuração visual do sistema"
    )
    
    idioma_atual = st.selectbox(
        "Idioma", 
        ["Português", "Inglês", "Espanhol"], 
        index=["Português", "Inglês", "Espanhol"].index(config.get("idioma", "Português")),
        help="Idioma da interface"
    )

with col2:
    timeout_atual = st.number_input(
        "Timeout da sessão (minutos)", 
        min_value=5, 
        max_value=120, 
        value=config.get("timeout_sessao", 30)
    )
    
    notificacoes_email = st.checkbox(
        "Notificações por email", 
        value=config.get("notificacoes_email", False),
        help="Receber alertas por email"
    )

servidor_smtp = ""
porta_smtp = 587
usuario_smtp = ""
senha_smtp = ""
ssl_smtp = True

if notificacoes_email:
    st.subheader("Configurações de Email")
    email_config = config.get("email_smtp", {})
    
    col1, col2 = st.columns(2)
    with col1:
        servidor_smtp = st.text_input(
            "Servidor SMTP", 
            value=email_config.get("servidor", ""),
            help="Ex: smtp.gmail.com"
        )
        porta_smtp = st.number_input(
            "Porta SMTP", 
            min_value=1, 
            max_value=65535, 
            value=email_config.get("porta", 587)
        )
    
    with col2:
        usuario_smtp = st.text_input(
            "Usuário SMTP", 
            value=email_config.get("usuario", ""),
            help="Seu email para envio"
        )
        senha_smtp = st.text_input(
            "Senha SMTP", 
            type="password",
            help="Senha do email ou app password"
        )
        
        ssl_smtp = st.checkbox(
            "Usar SSL/TLS", 
            value=email_config.get("ssl", True)
        )
    
    st.subheader("Testar Configurações de Email")
    email_teste = st.text_input("Email para teste", help="Digite um email para testar as configurações")
    
    if st.button("📧 Enviar Email de Teste"):
        if not email_teste:
            st.warning("Digite um email para teste.")
        elif not servidor_smtp or not usuario_smtp or not senha_smtp:
            st.error("Configure todas as informações SMTP antes de testar.")
        else:
            from email_utils import enviar_email_teste
            
            config_teste = {
                "servidor": servidor_smtp,
                "porta": porta_smtp,
                "usuario": usuario_smtp,
                "senha": senha_smtp,
                "ssl": ssl_smtp
            }
            
            with st.spinner("Enviando email de teste..."):
                sucesso = enviar_email_teste(email_teste, config_teste)
                
                if sucesso:
                    st.success("✅ Email de teste enviado com sucesso!")
                    log_atividade("Email de teste enviado", f"Destinatário: {email_teste}")
                else:
                    st.error("❌ Falha ao enviar email de teste. Verifique as configurações.")
                    log_atividade("Falha no teste de email", f"Destinatário: {email_teste}")

if st.button("💾 Salvar Configurações do Sistema"):
    nova_config = {
        "tema": tema_atual,
        "idioma": idioma_atual,
        "timeout_sessao": timeout_atual,
        "notificacoes_email": notificacoes_email,
        "email_smtp": {
            "servidor": servidor_smtp if notificacoes_email else "",
            "porta": porta_smtp if notificacoes_email else 587,
            "usuario": usuario_smtp if notificacoes_email else "",
            "senha": senha_smtp if notificacoes_email else "",
            "ssl": ssl_smtp if notificacoes_email else True
        }
    }
    
    salvar_configuracoes(nova_config)
    log_atividade("Configurações salvas", f"Tema: {tema_atual}, Idioma: {idioma_atual}, Timeout: {timeout_atual}min")
    st.success("Configurações salvas com sucesso!")
    st.rerun()

if st.session_state.get("username") == "admin":
    st.divider()
    st.subheader("🔧 Configurações Avançadas (Administrador)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Resetar Configurações", help="Restaurar configurações padrão"):
            if st.session_state.get("confirmar_reset"):
                resetar_configuracoes()
                st.success("Configurações resetadas com sucesso!")
                st.session_state.pop("confirmar_reset", None)
                st.rerun()
            else:
                st.session_state["confirmar_reset"] = True
                st.warning("⚠️ Clique novamente para confirmar o reset!")
    
    with col2:
        if st.button("🗑️ Limpar Cache", help="Limpar cache do sistema"):
            st.cache_data.clear()
            log_atividade("Cache limpo", "Cache do sistema foi limpo")
            st.success("Cache limpo com sucesso!")
    
    with col3:
        if st.button("📋 Logs do Sistema", help="Visualizar logs de atividade"):
            st.session_state["mostrar_logs"] = not st.session_state.get("mostrar_logs", False)

    if st.session_state.get("mostrar_logs", False):
        st.subheader("📋 Logs do Sistema")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text("Últimas atividades do sistema:")
        with col2:
            limite_logs = st.number_input("Limite de logs", min_value=10, max_value=500, value=50)
        
        logs = obter_logs_sistema(limite_logs)
        
        if logs:
            logs_text = "\n".join(logs)
            st.text_area("Logs", logs_text, height=300, disabled=True)
            
            st.download_button(
                label="📥 Baixar Logs",
                data=logs_text,
                file_name=f"logs_sistema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.info("Nenhum log encontrado.")

st.divider()
st.subheader("ℹ️ Informações do Sistema")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Usuário Atual", st.session_state.get("username", "N/A"))
    st.metric("Tema Ativo", config.get("tema", "Auto"))

with col2:
    if "login_time" in st.session_state:
        login_time = st.session_state.get("login_time")
        if isinstance(login_time, str):
            login_time = datetime.fromisoformat(login_time)
        tempo_sessao = datetime.now() - login_time
        st.metric("Tempo de Sessão", f"{int(tempo_sessao.total_seconds() // 60)} min")
    
    st.metric("Timeout Configurado", f"{config.get('timeout_sessao', 30)} min")

with col3:
    st.metric("Idioma", config.get("idioma", "Português"))
    st.metric("Notificações Email", "Ativadas" if config.get("notificacoes_email", False) else "Desativadas")