import streamlit as st
# Importa funções compartilhadas e estilo
from shared import carregar_autenticador, aplicar_estilo_solar
import streamlit_authenticator as stauth
import yaml, os
from streamlit_authenticator import Hasher

# --- CONFIGURAÇÃO DA PÁGINA ---
# Mudamos o ícone para um raio (mais técnico) e o título para SolarTrack
st.set_page_config(page_title="SolarTrack", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# Aplica o estilo global
aplicar_estilo_solar()

# CSS Específico para a Tela de Login e LOGO
st.markdown("""
<style>
    /* Ajuste para a imagem de capa ocupar altura total e ter bordas arredondadas */
    div[data-testid="stImage"] img {
        border-radius: 15px;
        object-fit: cover;
        max-height: 85vh;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.1);
    }
    /* Centraliza verticalmente a coluna da direita */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify_content: center;
    }
    /* Estilo da Logo em Texto */
    .logo-text {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 800;
        font-size: 3rem;
        color: #1E3A8A; /* Azul Escuro */
        margin-bottom: 0;
        letter-spacing: -1px;
    }
    .logo-suffix {
        color: #FF8C00; /* Laranja Solar */
    }
</style>
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
    # Título interno também atualizado
    st.title("SolarTrack - Dashboard")
    st.markdown("Bem-vindo ao sistema de **monitoramento e simulação fotovoltaica**.")
    st.markdown("---")

    # KPIs de Exemplo
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(label="Status do Sistema", value="Operacional", delta="Normal")
    with col2: st.metric(label="Alertas Ativos", value="0", delta="Estável") 
    with col3: st.metric(label="Exportações", value="Disponível", delta="Pronto")
    with col4: st.metric(label="Usuário", value=st.session_state.get("name", "Admin"), delta="Online")

    st.markdown("---")
    
    # Navegação Rápida
    st.subheader("🚀 Acesso Rápido")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🔋 Simulador", use_container_width=True): st.switch_page("pages/1_Simulador.py")
    with col2:
        if st.button("📊 Relatórios", use_container_width=True): st.switch_page("pages/3_Relatorios.py")
    with col3:
        if st.button("🚨 Alertas", use_container_width=True): st.switch_page("pages/5_Alertas.py")
    with col4:
        if st.button("📥 Exportação", use_container_width=True): st.switch_page("pages/4_Exportacao.py")
    with col5:
        if st.button("👤 Usuários", use_container_width=True): st.switch_page("pages/2_Cadastrar_Usuario.py")

    # Sidebar
    st.sidebar.success("✅ SolarTrack Online")
    st.sidebar.divider()
    if st.sidebar.button("🔓 Sair / Logout"):
        realizar_logout()

# ==========================================
#           TELA DE LOGIN (NOVO DESIGN)
# ==========================================
else:
    # Layout de Duas Colunas
    col_hero, col_login_wrapper = st.columns([1.3, 1], gap="large")
    
    # --- COLUNA ESQUERDA: IMAGEM HERO ---
    with col_hero:
        # Nova imagem: Mais tecnológica e moderna (Painéis azuis profundos)
        st.image("https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?q=80&w=1974&auto=format&fit=crop")

    # --- COLUNA DIREITA: FORMULÁRIO ---
    with col_login_wrapper:
        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
        
        # LOGO ESTILIZADA (Sem emoji, visual de marca)
        st.markdown("""
            <div style="margin-bottom: 20px;">
                <span class="logo-text">Solar<span class="logo-suffix">Track</span></span>
                <p style="color: gray; font-size: 1.1rem; margin-top: -10px;">Gestão Inteligente de Energia</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Container Card para o Login
        with st.container(border=True):
            # Abas para separar Entrar de Cadastrar
            tab_entrar, tab_criar = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
            
            # --- ABA 1: LOGIN ---
            with tab_entrar:
                authenticator = carregar_autenticador()
                try:
                    authenticator.login(location="main")
                except Exception as e:
                    st.error(f"Erro ao carregar login: {e}")

                if st.session_state.get("authentication_status"):
                    st.session_state["logged_in"] = True
                    st.rerun()
                elif st.session_state.get("authentication_status") is False:
                    st.error("❌ Usuário ou senha incorretos.")
                elif st.session_state.get("authentication_status") is None:
                    st.info("Digite suas credenciais para acessar o painel.")

            # --- ABA 2: CADASTRO ---
            with tab_criar:
                st.markdown("Preencha os dados para novo acesso.")
                novo_nome = st.text_input("Nome", key="reg_nome")
                novo_email = st.text_input("Email", key="reg_email")
                novo_user = st.text_input("Usuário", key="reg_user")
                novo_pass = st.text_input("Senha", type="password", key="reg_pass")
                
                if st.button("Criar Acesso", type="primary", use_container_width=True):
                    # Lógica de cadastro
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
                            st.success("Conta criada com sucesso!")

        # Rodapé simples
        st.markdown("""
        <div style="text-align: center; color: #bbb; font-size: 11px; margin-top: 30px;">
            SolarTrack System v2.1 • Desenvolvido para Alta Performance
        </div>
        """, unsafe_allow_html=True)