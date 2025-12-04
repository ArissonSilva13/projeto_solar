import streamlit as st
# Importa funções compartilhadas e estilo
from shared import carregar_autenticador, aplicar_estilo_solar
import streamlit_authenticator as stauth
import yaml, os
from streamlit_authenticator import Hasher

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SolarTrack", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# Aplica o estilo global
aplicar_estilo_solar()

# --- CSS E HELPERS VISUAIS ---
st.markdown("""
<style>
    /* Imagem de Capa Login */
    div[data-testid="stImage"] img {
        border-radius: 12px;
        object-fit: cover;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    /* Alinhamento da Coluna de Login */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify_content: center;
    }
    /* Logo em Texto */
    .logo-text {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        color: #1E3A8A;
        letter-spacing: -1px;
    }
    .logo-suffix { color: #FF8C00; }
</style>
""", unsafe_allow_html=True)

# Função para renderizar ícones SVG (Padrão Industrial)
def render_icon(svg_path, title, color="#1E3A8A"):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            {svg_path}
        </svg>
        <h4 style="margin: 0; color: #1E3A8A; font-weight: 600; font-family: sans-serif;">{title}</h4>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESSÃO ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def realizar_logout():
    for chave in list(st.session_state.keys()):
        del st.session_state[chave]
    st.rerun()

# ==========================================
#              ÁREA LOGADA (DASHBOARD)
# ==========================================
if st.session_state.get("logged_in"):
    # Título Principal
    st.title("SolarTrack - Visão Geral")
    st.markdown("Painel de controle operacional e administrativo.")
    st.markdown("---")

    # --- KPIs DE STATUS (SEM EMOJIS) ---
    # SVG: Activity/Pulse
    render_icon('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>', "Status do Sistema")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(label="Status Operacional", value="Online", delta="Normal")
        with col2: st.metric(label="Alertas Pendentes", value="0", delta="Estável") 
        with col3: st.metric(label="Serviço de Exportação", value="Ativo", delta="Pronto")
        with col4: st.metric(label="Usuário Logado", value=st.session_state.get("name", "Admin"), delta="Conectado")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO RÁPIDA (BOTÕES LIMPOS) ---
    # SVG: Grid/Menu
    render_icon('<rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect>', "Módulos do Sistema")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Simulador de Produção", use_container_width=True): st.switch_page("pages/1_Simulador.py")
    with col2:
        if st.button("Relatórios & BI", use_container_width=True): st.switch_page("pages/3_Relatorios.py")
    with col3:
        if st.button("Central de Monitoramento", use_container_width=True): st.switch_page("pages/5_Alertas.py")
    with col4:
        if st.button("Exportação de Dados", use_container_width=True): st.switch_page("pages/4_Exportacao.py")
    with col5:
        if st.button("Gestão de Acessos", use_container_width=True): st.switch_page("pages/2_Cadastrar_Usuario.py")

    # Sidebar Limpa
    st.sidebar.markdown("### Menu Principal")
    if st.sidebar.button("Encerrar Sessão", type="primary"):
        realizar_logout()

# ==========================================
#           TELA DE LOGIN (CLEAN)
# ==========================================
else:
    col_hero, col_login_wrapper = st.columns([1.3, 1], gap="large")
    
    # Coluna Esquerda: Imagem Tech
    with col_hero:
        st.image("https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?q=80&w=1974&auto=format&fit=crop")

    # Coluna Direita: Login Clean
    with col_login_wrapper:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logo Texto
        st.markdown("""
            <div style="margin-bottom: 25px;">
                <span class="logo-text">Solar<span class="logo-suffix">Track</span></span>
                <p style="color: #64748B; font-size: 1.1rem; margin-top: -5px;">Gestão Inteligente de Energia</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            tab_entrar, tab_criar = st.tabs(["Acessar Conta", "Solicitar Acesso"])
            
            with tab_entrar:
                authenticator = carregar_autenticador()
                try:
                    # Correção: location='main' e tratamento de erro sem desempacotar retorno
                    authenticator.login(location="main")
                except Exception as e:
                    # Em caso de erro interno, apenas loga e continua ou avisa se crítico
                    # st.error(f"Erro no módulo de autenticação: {e}") 
                    pass

                if st.session_state.get("authentication_status"):
                    st.session_state["logged_in"] = True
                    st.rerun()
                elif st.session_state.get("authentication_status") is False:
                    st.error("Credenciais inválidas.")
                elif st.session_state.get("authentication_status") is None:
                    st.info("Insira suas credenciais corporativas.")

            with tab_criar:
                st.caption("Preencha os dados para novo acesso administrativo.")
                novo_nome = st.text_input("Nome Completo", key="reg_nome")
                novo_email = st.text_input("Email Corporativo", key="reg_email")
                novo_user = st.text_input("Usuário", key="reg_user")
                novo_pass = st.text_input("Senha", type="password", key="reg_pass")
                
                if st.button("Criar Conta", type="primary", use_container_width=True):
                    ARQUIVO = "painel_admin/usuarios.yaml"
                    if not os.path.exists(ARQUIVO): ARQUIVO = "usuarios.yaml"
                    
                    if not novo_nome or not novo_user or not novo_pass:
                        st.warning("Preencha todos os campos obrigatórios.")
                    else:
                        if os.path.exists(ARQUIVO):
                            with open(ARQUIVO, "r") as f:
                                dados = yaml.safe_load(f) or {}
                        else:
                            dados = {}
                        
                        dados.setdefault("usernames", {})
                        if novo_user in dados["usernames"]:
                            st.error("Usuário já existe.")
                        else:
                            hashed_pwd = Hasher([novo_pass]).generate()[0]
                            dados["usernames"][novo_user] = {
                                "name": novo_nome,
                                "email": novo_email,
                                "password": hashed_pwd
                            }
                            with open(ARQUIVO, "w") as f:
                                yaml.dump(dados, f)
                            st.success("Conta criada! Acesse a aba de login.")

        st.markdown("""
        <div style="text-align: center; color: #94A3B8; font-size: 11px; margin-top: 30px;">
            SolarTrack System v2.1 • Enterprise Edition
        </div>
        """, unsafe_allow_html=True)