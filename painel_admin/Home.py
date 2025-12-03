import streamlit as st
# 1. ADICIONADO: Importamos a função de estilo aqui
from shared import carregar_autenticador, aplicar_estilo_solar
import streamlit_authenticator as stauth
import yaml, os
from streamlit_authenticator import Hasher

# Configuração da página
st.set_page_config(page_title="Início", page_icon="☀️", layout="wide", initial_sidebar_state="collapsed")

# 2. ADICIONADO: Chamamos a função para aplicar a "maquiagem" CSS
aplicar_estilo_solar()

# --- Lógica de Sessão e Logout ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def realizar_logout():
    for chave in list(st.session_state.keys()):
        del st.session_state[chave]
    st.rerun()

# --- CONTEÚDO PRINCIPAL ---
if st.session_state.get("logged_in"):
    st.title("☀️ Painel Solar - Monitoramento Inteligente")

    st.markdown("""
    Bem-vindo ao sistema de **monitoramento e simulação fotovoltaica**. 
    Acompanhe abaixo o status geral do sistema e utilize o menu para acessar as ferramentas detalhadas.
    """)

    st.markdown("---")

    # --- AQUI ESTÁ A GRANDE MUDANÇA VISUAL ---
    # Substituímos aquele HTML manual feio por Métricas Nativas
    # O CSS do shared.py vai transformar isso em CARDs bonitos automaticamente
    st.subheader("📊 Status do Sistema em Tempo Real")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Status do Sistema", value="Operacional", delta="Normal")
    
    with col2:
        # Delta invertido para mostrar alerta
        st.metric(label="Alertas Ativos", value="2", delta="-1 Crítico", delta_color="inverse") 
        
    with col3:
        st.metric(label="Exportações", value="Disponível", delta="Pronto")
        
    with col4:
        st.metric(label="Usuários Ativos", value="Sistema", delta="Online")

    st.markdown("---")
    
    # --- ÁREA DE NAVEGAÇÃO (Mantida, mas organizada) ---
    st.subheader("🚀 Acesso Rápido")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🔋 Simulador", use_container_width=True):
            st.switch_page("pages/1_Simulador.py")
    with col2:
        if st.button("📊 Relatórios", use_container_width=True):
            st.switch_page("pages/3_Relatorios.py")
    with col3:
        if st.button("🚨 Alertas", use_container_width=True):
            st.switch_page("pages/5_Alertas.py")
    with col4:
        if st.button("📥 Exportação", use_container_width=True):
            st.switch_page("pages/4_Exportacao.py")
    with col5:
        if st.button("👤 Usuários", use_container_width=True):
            st.switch_page("pages/2_Cadastrar_Usuario.py")

    st.markdown("---")

    # --- DETALHES (Expander) ---
    # Mantive seus textos, apenas limpei a estrutura
    with st.expander("ℹ️ Detalhes das Funcionalidades", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Simulação", "Relatórios", "Alertas"])
        
        with tab1:
            st.markdown("""
            **Simulação Avançada:**
            - Produção em tempo real e Consumo inteligente
            - Análise de excedentes e Parâmetros ajustáveis
            """)
        
        with tab2:
            st.markdown("""
            **Relatórios Detalhados:**
            - Resumo geral e Análise detalhada (Plotly)
            - Comparativo mensal e Performance
            """)
            
        with tab3:
            st.markdown("""
            **Sistema de Alertas:**
            - Monitoramento em tempo real e Déficits críticos
            - Recomendações inteligentes
            """)

    # --- BARRA LATERAL ---
    st.sidebar.success("✅ Sistema Online")
    st.sidebar.markdown("### 🧭 Menu Principal")
    st.sidebar.page_link("pages/1_Simulador.py", label="🔋 Simulador")
    st.sidebar.page_link("pages/3_Relatorios.py", label="📊 Relatórios")
    st.sidebar.page_link("pages/5_Alertas.py", label="🚨 Alertas")
    st.sidebar.page_link("pages/4_Exportacao.py", label="📥 Exportação")
    st.sidebar.page_link("pages/Ajustes.py", label="🛠️ Ajustes")
    
    st.sidebar.divider()
    if st.sidebar.button("🔓 Sair / Logout"):
        realizar_logout()

# --- LÓGICA DE LOGIN (Mantida igual para não quebrar nada) ---
else:
    # Colunas para centralizar o login na tela (fica mais bonito)
    col_vazia_esq, col_login, col_vazia_dir = st.columns([1, 2, 1])
    
    with col_login:
        menu = st.radio("Acesso", ["Login", "Cadastrar"], horizontal=True)

        if menu == "Login":
            st.markdown("### 🔐 Acesso ao Sistema")
            authenticator = carregar_autenticador()
            authenticator.login(fields={'Form name': ' ', 'Username': 'Usuário', 'Password': 'Senha'})

            name = st.session_state.get("name")
            auth_status = st.session_state.get("authentication_status")

            if auth_status:
                st.session_state["logged_in"] = True
                st.rerun() # Recarrega para entrar no painel

            elif auth_status is False:
                st.error("❌ Usuário ou senha incorretos")
            elif auth_status is None:
                st.warning("Por favor, insira suas credenciais")

        elif menu == "Cadastrar":
            st.markdown("### 📝 Novo Cadastro")
            nome = st.text_input("Nome completo")
            email = st.text_input("Email")
            usuario = st.text_input("Usuário (login)")
            senha = st.text_input("Senha", type="password")

            if st.button("Cadastrar", type="primary"):
                ARQUIVO = "painel_admin/usuarios.yaml"
                if not nome or not email or not usuario or not senha:
                    st.warning("Preencha todos os campos.")
                else:
                    if os.path.exists(ARQUIVO):
                        with open(ARQUIVO, "r") as f:
                            dados = yaml.safe_load(f) or {}
                    else:
                        dados = {}
                    dados.setdefault("usernames", {})

                    if usuario in dados["usernames"]:
                        st.error("Usuário já existe.")
                    else:
                        hashed_pwd = Hasher([senha]).generate()[0]
                        dados["usernames"][usuario] = {
                            "name": nome,
                            "email": email,
                            "password": hashed_pwd
                        }
                        with open(ARQUIVO, "w") as f:
                            yaml.dump(dados, f)
                        st.success(f"Usuário '{usuario}' cadastrado! Faça login.")