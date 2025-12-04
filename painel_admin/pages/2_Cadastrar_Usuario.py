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
st.set_page_config(page_title="Gestão de Usuários", page_icon="⚡", layout="wide")
aplicar_estilo_solar()

# --- CONSTANTES ---
# Tenta localizar o arquivo corretamente dependendo de onde o script é rodado
ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"
if not os.path.exists("painel_admin"):
    # Fallback se rodar de dentro da pasta painel_admin
    ARQUIVO_USUARIOS = "usuarios.yaml"

# --- VALIDAÇÃO DE LOGIN ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error(" Acesso restrito. Por favor, faça login.")
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

# --- CABEÇALHO ---
st.title("Gestão de Acesso")
st.markdown("Administração de credenciais e visualização da equipe ativa.")

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

# --- VERIFICAÇÃO INICIAL ---
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
             pass 
             
    except Exception as e:
        st.error(f"Erro de leitura: {e}")

verificar_alertas_sistema()

# --- LAYOUT PRINCIPAL ---
col_cadastro, col_lista = st.columns([1, 1.5], gap="large")

# === COLUNA 1: FORMULÁRIO DE CADASTRO ===
with col_cadastro:
    # SVG: User Plus (Novo Cadastro)
    render_icon('<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line>', "Novo Usuário")
    
    # Card visual para o formulário
    with st.container(border=True):
        st.caption("Preencha os dados para conceder acesso ao sistema.")
        
        nome = st.text_input("Nome Completo", placeholder="Ex: João Silva")
        email = st.text_input("E-mail Corporativo", placeholder="joao@solar.com")
        
        c1, c2 = st.columns(2)
        usuario = c1.text_input("Login", placeholder="joaosilva")
        senha = c2.text_input("Senha Provisória", type="password")
        
        st.markdown("---")
        
        # Botão sem emoji, texto limpo
        if st.button("Cadastrar Usuário", type="primary", use_container_width=True):
            if not nome or not email or not usuario or not senha:
                st.warning("Todos os campos são obrigatórios.")
            else:
                dados = carregar_dados_usuarios()
                dados.setdefault("usernames", {})

                if usuario in dados["usernames"]:
                    st.error("Este nome de usuário já está em uso.")
                else:
                    try:
                        hashed_pwd = Hasher([senha]).generate()[0]
                        dados["usernames"][usuario] = {
                            "name": nome,
                            "email": email,
                            "password": hashed_pwd
                        }
                        
                        salvar_usuario(dados)
                        
                        st.success(f"Usuário {usuario} cadastrado com sucesso.")
                        
                        # Notificação silenciosa
                        notificacao_system.adicionar_notificacao(
                            'usuario_criado',
                            'Novo Acesso',
                            f'Usuário {usuario} criado por {st.session_state.get("username", "Admin")}.',
                            'baixa'
                        )
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# === COLUNA 2: LISTA DE USUÁRIOS ===
with col_lista:
    # SVG: Users (Equipe)
    render_icon('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>', "Equipe Cadastrada")
    
    dados_atuais = carregar_dados_usuarios()
    df_users = get_tabela_usuarios(dados_atuais)
    
    if not df_users.empty:
        # Métricas rápidas em card
        with st.container(border=True):
            k1, k2 = st.columns(2)
            k1.metric("Total de Usuários", len(df_users))
            k2.metric("Status do Sistema", "Online", delta="Seguro")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tabela Profissional
        st.dataframe(
            df_users,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Usuário": st.column_config.TextColumn(
                    "Login",
                    help="ID de acesso",
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
                    "Situação",
                    width="small"
                )
            }
        )
        
        with st.expander("Informações de Segurança"):
            st.info("""
            As senhas são armazenadas utilizando criptografia hash unidirecional. 
            Não é possível recuperar senhas antigas, apenas redefini-las via administrador.
            """)
            
    else:
        st.info("Nenhum usuário encontrado na base de dados.")

# --- RODAPÉ DA SIDEBAR ---
st.sidebar.divider()
# Tenta renderizar painel de notificações se existir
try:
    notificacao_system.exibir_painel_notificacoes()
    notificacao_system.auto_refresh_alertas()
    notificacao_system.limpar_notificacoes_antigas()
except:
    pass