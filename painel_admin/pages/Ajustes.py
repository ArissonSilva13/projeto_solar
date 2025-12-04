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

from shared import aplicar_estilo_solar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Configurações", page_icon="⚡", layout="wide")
aplicar_estilo_solar()

# --- SETUP DE LOGGING ---
if not os.path.exists("painel_admin/logs"):
    os.makedirs("painel_admin/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(username)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("painel_admin/logs/sistema.log"),
        logging.StreamHandler()
    ]
)

# --- VALIDAÇÃO DE LOGIN ---
if not st.session_state.get("logged_in"):
    st.error(" Acesso restrito. Faça login.")
    st.stop()

# --- HELPER PARA ÍCONES SVG ---
def render_icon(svg_path, title, color="#1E3A8A"):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            {svg_path}
        </svg>
        <h4 style="margin: 0; color: #1E3A8A; font-weight: 600; font-family: sans-serif;">{title}</h4>
    </div>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE LÓGICA (RESTAURADAS) ---
def aplicar_tema(tema: str):
    """Aplica cores de fundo via CSS conforme a seleção do usuário."""
    if tema == "Escuro":
        st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        .stSelectbox > div > div { background-color: #262730; color: #ffffff; }
        .stTextInput > div > div > input { background-color: #262730; color: #ffffff; }
        </style>
        """, unsafe_allow_html=True)
    elif tema == "Claro":
        st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
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
        "email_smtp": {"servidor": "", "porta": 587, "usuario": "", "senha": "", "ssl": True}
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
    if "login_time" not in st.session_state: return False
    config = carregar_configuracoes()
    timeout_minutos = config.get("timeout_sessao", 30)
    login_time = st.session_state.get("login_time")
    if isinstance(login_time, str): login_time = datetime.fromisoformat(login_time)
    
    if datetime.now() > login_time + timedelta(minutes=timeout_minutos):
        st.session_state.clear()
        st.error("Sessão expirada.")
        st.rerun()
    return True

def resetar_configuracoes():
    config_padrao = {
        "tema": "Auto", "idioma": "Português", "timeout_sessao": 30, 
        "notificacoes_email": False, 
        "email_smtp": {"servidor": "", "porta": 587, "usuario": "", "senha": "", "ssl": True}
    }
    salvar_configuracoes(config_padrao)
    log_atividade("Reset", "Configurações restauradas para padrão")

def verificar_senha_atual(senha_atual: str, username: str) -> bool:
    dados_usuarios = carregar_usuarios()
    if username not in dados_usuarios.get("usernames", {}): return False
    senha_hash = dados_usuarios["usernames"][username]["password"]
    hasher = Hasher([senha_atual])
    return hasher.check([senha_hash], [senha_atual])[0]

def obter_logs_sistema(limite: int = 50) -> list:
    log_file = "painel_admin/logs/sistema.log"
    if not os.path.exists(log_file): return []
    with open(log_file, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f.readlines()[-limite:]]

ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"
if not os.path.exists("painel_admin"): ARQUIVO_USUARIOS = "usuarios.yaml"

@st.cache_data
def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, "w") as f:
        yaml.dump(dados, f, default_flow_style=False)

# --- EXECUÇÃO ---
verificar_timeout_sessao()
config = carregar_configuracoes()
aplicar_tema(config.get("tema", "Auto")) # Funcionalidade de tema restaurada

st.title("Painel de Controle")
st.markdown("Gerenciamento de perfil, preferências globais e manutenção do sistema.")

# --- SEÇÃO 1: PERFIL DO USUÁRIO ---
render_icon('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>', "Meu Perfil")

dados_usuarios = carregar_usuarios()
usuario_atual = st.session_state.get("username")

if usuario_atual and usuario_atual in dados_usuarios.get("usernames", {}):
    user_data = dados_usuarios["usernames"][usuario_atual]
    
    with st.container(border=True):
        tabs_perfil = st.tabs(["Dados Pessoais", "Segurança"])
        
        with tabs_perfil[0]:
            col1, col2 = st.columns(2)
            novo_nome = col1.text_input("Nome completo", value=user_data.get("name", ""))
            novo_email = col2.text_input("Email Corporativo", value=user_data.get("email", ""))
            
            if st.button("Atualizar Perfil", type="primary"):
                if novo_nome and novo_email:
                    dados_usuarios["usernames"][usuario_atual]["name"] = novo_nome
                    dados_usuarios["usernames"][usuario_atual]["email"] = novo_email
                    salvar_usuarios(dados_usuarios)
                    log_atividade("Perfil atualizado", f"User: {usuario_atual}")
                    st.success("Dados atualizados com sucesso.")
                    st.rerun()
                else:
                    st.warning("Preencha todos os campos.")
        
        with tabs_perfil[1]:
            c1, c2, c3 = st.columns(3)
            senha_atual = c1.text_input("Senha Atual", type="password")
            nova_senha = c2.text_input("Nova Senha", type="password")
            confirmar_senha = c3.text_input("Confirmar Senha", type="password")
            
            if st.button("Definir Nova Senha"):
                if not senha_atual or not nova_senha:
                    st.warning("Preencha os campos de senha.")
                elif not verificar_senha_atual(senha_atual, usuario_atual):
                    st.error("A senha atual informada está incorreta.")
                elif nova_senha != confirmar_senha:
                    st.error("A confirmação da senha não coincide.")
                elif len(nova_senha) < 4:
                    st.error("A nova senha deve ter no mínimo 4 caracteres.")
                else:
                    nova_senha_hash = Hasher([nova_senha]).generate()[0]
                    dados_usuarios["usernames"][usuario_atual]["password"] = nova_senha_hash
                    salvar_usuarios(dados_usuarios)
                    log_atividade("Senha alterada", "Usuário alterou a própria senha")
                    st.success("Senha alterada com segurança.")

st.markdown("<br>", unsafe_allow_html=True)

# --- SEÇÃO 2: CONFIGURAÇÕES DO SISTEMA ---
render_icon('<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>', "Preferências Globais")

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        tema_atual = st.selectbox("Tema da Interface", ["Claro", "Escuro", "Auto"], index=["Claro", "Escuro", "Auto"].index(config.get("tema", "Auto")))
        idioma_atual = st.selectbox("Idioma", ["Português", "Inglês", "Espanhol"], index=["Português", "Inglês", "Espanhol"].index(config.get("idioma", "Português")))
    
    with col2:
        timeout_atual = st.number_input("Timeout de Sessão (minutos)", 5, 120, config.get("timeout_sessao", 30))
        notificacoes_email = st.toggle("Habilitar Notificações via Email", value=config.get("notificacoes_email", False))

    # Configuração de Email Condicional
    servidor_smtp, porta_smtp, usuario_smtp, senha_smtp, ssl_smtp = "", 587, "", "", True
    
    if notificacoes_email:
        st.markdown("##### 📧 Configuração SMTP")
        email_config = config.get("email_smtp", {})
        c1, c2 = st.columns(2)
        servidor_smtp = c1.text_input("Servidor", value=email_config.get("servidor", ""))
        porta_smtp = c2.number_input("Porta", value=email_config.get("porta", 587))
        usuario_smtp = c1.text_input("Usuário", value=email_config.get("usuario", ""))
        senha_smtp = c2.text_input("Senha / App Key", type="password", help="Use a senha de aplicativo para maior segurança")
        ssl_smtp = st.checkbox("Usar SSL/TLS", value=email_config.get("ssl", True))
        
        email_teste = st.text_input("Email para teste de envio")
        if st.button("Enviar Teste de Conexão"):
            if not email_teste:
                st.warning("Digite um email para teste.")
            elif not servidor_smtp or not usuario_smtp or not senha_smtp:
                st.error("Configure todas as informações SMTP antes de testar.")
            else:
                # Funcionalidade de teste real restaurada
                try:
                    from email_utils import enviar_email_teste
                    config_teste = {
                        "servidor": servidor_smtp, "porta": porta_smtp,
                        "usuario": usuario_smtp, "senha": senha_smtp, "ssl": ssl_smtp
                    }
                    with st.spinner("Enviando email de teste..."):
                        sucesso = enviar_email_teste(email_teste, config_teste)
                        if sucesso:
                            st.success("✅ Email de teste enviado com sucesso!")
                            log_atividade("Email de teste enviado", f"Destinatário: {email_teste}")
                        else:
                            st.error("❌ Falha no envio. Verifique as credenciais.")
                            log_atividade("Falha no teste de email", f"Destinatário: {email_teste}")
                except ImportError:
                    st.error("Módulo 'email_utils' não encontrado.")

    st.markdown("---")
    if st.button("Salvar Configurações", type="primary", use_container_width=True):
        nova_config = {
            "tema": tema_atual, "idioma": idioma_atual, "timeout_sessao": timeout_atual,
            "notificacoes_email": notificacoes_email,
            "email_smtp": {"servidor": servidor_smtp, "porta": porta_smtp, "usuario": usuario_smtp, "senha": senha_smtp, "ssl": ssl_smtp}
        }
        salvar_configuracoes(nova_config)
        log_atividade("Configurações salvas")
        st.success("Preferências atualizadas com sucesso!")
        st.rerun()

# --- SEÇÃO 3: ADMINISTRAÇÃO (Apenas Admin) ---
if st.session_state.get("username") == "admin":
    st.markdown("<br>", unsafe_allow_html=True)
    render_icon('<rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line>', "Administração do Sistema", "#FF8C00")
    
    with st.expander("Ferramentas de Manutenção", expanded=False):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            if st.button("Restaurar Padrões", use_container_width=True):
                # Mantida lógica de confirmação original via session_state
                if st.session_state.get("confirmar_reset"):
                    resetar_configuracoes()
                    st.success("Sistema resetado.")
                    st.session_state.pop("confirmar_reset", None)
                    st.rerun()
                else:
                    st.session_state["confirmar_reset"] = True
                    st.warning("Clique novamente para confirmar.")
        
        with c2:
            if st.button("Limpar Cache de Dados", use_container_width=True):
                st.cache_data.clear()
                log_atividade("Cache limpo")
                st.success("Cache esvaziado.")
        
        with c3:
            if st.button("Ver Logs de Auditoria", use_container_width=True):
                st.session_state["mostrar_logs"] = not st.session_state.get("mostrar_logs", False)

    if st.session_state.get("mostrar_logs", False):
        logs = obter_logs_sistema(50)
        st.caption("Últimos 50 registros de atividade:")
        if logs:
            st.code("\n".join(logs), language="text")
            st.download_button("Baixar Log Completo", "\n".join(logs), "sistema.log")
        else:
            st.info("Log vazio.")

# --- FOOTER ---
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Usuário", st.session_state.get("username", "N/A"))
if "login_time" in st.session_state:
    l_time = st.session_state.get("login_time")
    if isinstance(l_time, str): l_time = datetime.fromisoformat(l_time)
    c2.metric("Sessão Ativa", f"{int((datetime.now() - l_time).total_seconds() // 60)} min")
c3.metric("Versão", "2.1.0")