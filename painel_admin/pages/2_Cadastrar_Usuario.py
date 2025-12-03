import streamlit as st
import yaml
import os
import sys
import pandas as pd
from streamlit_authenticator import Hasher

# Adiciona o diretório raiz para importações
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Tenta importar notificações (Fallback para evitar erro se arquivo não existir)
try:
    from painel_admin.notificacoes import NotificacaoRealTime
except ImportError:
    try:
        from notificacoes import NotificacaoRealTime
    except:
        # Mock class se tudo falhar
        class NotificacaoRealTime:
            def adicionar_notificacao(self, *args): pass
            def exibir_painel_notificacoes(self): pass
            def auto_refresh_alertas(self): pass
            def limpar_notificacoes_antigas(self): pass

from shared import aplicar_estilo_solar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Usuários", page_icon="👤", layout="wide")
aplicar_estilo_solar()

# --- CONSTANTES ---
# Tenta localizar o arquivo corretamente dependendo de onde o script é rodado
ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"
if not os.path.exists("painel_admin"):
    # Fallback se rodar de dentro da pasta painel_admin
    ARQUIVO_USUARIOS = "usuarios.yaml"

# --- VALIDAÇÃO DE LOGIN ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Acesso restrito. Por favor, faça login.")
    st.stop()

st.title("👤 Gestão de Acesso e Usuários")
st.markdown("Cadastre novos administradores e visualize a equipe ativa.")

notificacao_system = NotificacaoRealTime()

# --- FUNÇÕES AUXILIARES ---
def carregar_dados_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def salvar_usuario(dados):
    with open(ARQUIVO_USUARIOS, "w") as f:
        yaml.dump(dados, f, default_flow_style=False)

def get_tabela_usuarios(dados):
    if "usernames" not in dados:
        return pd.DataFrame()
    
    lista = []
    for user, info in dados["usernames"].items():
        lista.append({
            "Usuário": user,
            "Nome": info.get("name", ""),
            "Email": info.get("email", ""),
            "Status": "Ativo" # Simulação
        })
    return pd.DataFrame(lista)

# --- VERIFICAÇÃO INICIAL (Mantendo sua lógica de alertas) ---
def verificar_alertas_sistema():
    if not os.path.exists(ARQUIVO_USUARIOS):
        notificacao_system.adicionar_notificacao(
            'sistema', 'Arquivo Ausente', 'Arquivo de usuários recriado.', 'baixa'
        )
    
    try:
        dados = carregar_dados_usuarios()
        num_usuarios = len(dados.get("usernames", {}))
        
        if num_usuarios == 0:
            notificacao_system.adicionar_notificacao(
                'sistema', 'Sem Usuários', 'Crie um usuário imediatamente.', 'media'
            )
        elif num_usuarios > 10:
             # Apenas log silencioso ou warning leve
             pass 
             
    except Exception as e:
        st.error(f"Erro de leitura: {e}")

verificar_alertas_sistema()

# --- LAYOUT PRINCIPAL ---
col_cadastro, col_lista = st.columns([1, 1.5], gap="large")

# === COLUNA 1: FORMULÁRIO DE CADASTRO ===
with col_cadastro:
    st.subheader("✨ Novo Cadastro")
    
    # Card visual para o formulário
    with st.container(border=True):
        st.markdown("Preencha os dados abaixo para conceder acesso.")
        
        nome = st.text_input("Nome Completo", placeholder="Ex: João Silva")
        email = st.text_input("E-mail Corporativo", placeholder="joao@solar.com")
        
        c1, c2 = st.columns(2)
        usuario = c1.text_input("Usuário (Login)", placeholder="joaosilva")
        senha = c2.text_input("Senha Provisória", type="password")
        
        st.markdown("---")
        
        if st.button("✅ Cadastrar Usuário", type="primary", use_container_width=True):
            if not nome or not email or not usuario or not senha:
                st.warning("⚠️ Todos os campos são obrigatórios.")
            else:
                dados = carregar_dados_usuarios()
                dados.setdefault("usernames", {})

                if usuario in dados["usernames"]:
                    st.error("❌ Este nome de usuário já está em uso.")
                else:
                    try:
                        hashed_pwd = Hasher([senha]).generate()[0]
                        dados["usernames"][usuario] = {
                            "name": nome,
                            "email": email,
                            "password": hashed_pwd
                        }
                        
                        salvar_usuario(dados)
                        
                        st.success(f"🎉 Usuário **{usuario}** cadastrado com sucesso!")
                        st.balloons()
                        
                        # Notificação
                        notificacao_system.adicionar_notificacao(
                            'usuario_criado',
                            'Novo Acesso',
                            f'Usuário {usuario} criado por {st.session_state.get("username", "Admin")}.',
                            'baixa'
                        )
                        
                        # Limpa campos (gambiarra visual do streamlit forçando rerun)
                        # st.rerun() # Opcional: descomente se quiser limpar o form
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# === COLUNA 2: LISTA DE USUÁRIOS ===
with col_lista:
    st.subheader("👥 Equipe Cadastrada")
    
    dados_atuais = carregar_dados_usuarios()
    df_users = get_tabela_usuarios(dados_atuais)
    
    if not df_users.empty:
        # Métricas rápidas
        k1, k2 = st.columns(2)
        k1.metric("Total de Usuários", len(df_users))
        k2.metric("Status do Sistema", "Online", delta="Seguro")
        
        st.markdown("") # Espaçamento
        
        # Tabela Bonita
        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Usuário": st.column_config.TextColumn(
                    "Login",
                    help="Nome usado para entrar no sistema",
                    width="medium"
                ),
                "Nome": st.column_config.TextColumn(
                    "Nome Completo",
                    width="large"
                ),
                "Email": st.column_config.TextColumn(
                    "Contato"
                ),
                "Status": st.column_config.Column(
                    "Status",
                    width="small"
                )
            }
        )
        
        with st.expander("ℹ️ Informações de Segurança"):
            st.info("""
            - As senhas são armazenadas com criptografia (Hash).
            - Não é possível visualizar a senha atual de um usuário.
            - Para alterar uma senha, é necessário contatar o suporte de TI (ou editar o YAML manualmente se tiver acesso ao servidor).
            """)
            
    else:
        st.info("Nenhum usuário encontrado na base de dados.")

# --- RODAPÉ DA SIDEBAR ---
st.sidebar.divider()
notificacao_system.exibir_painel_notificacoes()
notificacao_system.auto_refresh_alertas()
notificacao_system.limpar_notificacoes_antigas()