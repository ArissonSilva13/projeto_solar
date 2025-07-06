import streamlit as st
from shared import carregar_autenticador
import streamlit_authenticator as stauth
import yaml, os
from streamlit_authenticator import Hasher

st.set_page_config(page_title="Início", page_icon="☀️", initial_sidebar_state="collapsed")

# ✅ Garante que 'logged_in' esteja sempre definido
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 🔁 Função para logout completo e seguro
def realizar_logout():
    for chave in list(st.session_state.keys()):
        del st.session_state[chave]
    st.rerun()

# ✅ Verifica se está logado
if st.session_state.get("logged_in"):
    st.title("☀️ Painel Solar - Início")

    st.markdown("""
    Bem-vindo ao sistema de **monitoramento e simulação de produção de energia solar**.

    Este painel permite que você:
    - 🔋 Simule produção e consumo de energia.
    - 📊 Visualize excedentes por hora.
    - ⚙️ Configure parâmetros de geração e consumo.

    Use o menu lateral para navegar entre as funcionalidades.
    """)

    st.sidebar.success("Você está logado.")
    st.sidebar.page_link("pages/1_Simulador.py", label="🔋 Ir para Simulador")
    st.sidebar.page_link("pages/2_Configuracoes.py", label="⚙️ Ir para Configurações")
    st.sidebar.page_link("pages/Ajustes.py", label="🛠️ Ir para Ajustes")

    if st.sidebar.button("🔓 Logout"):
        realizar_logout()

else:
    menu = st.sidebar.radio("Menu", ["Login", "Cadastrar"])

    if menu == "Login":
        st.title("🔐 Login")
        authenticator = carregar_autenticador()

        authenticator.login(fields={'Form name': 'Login', 'Username': 'Usuário', 'Password': 'Senha'})

        name = st.session_state.get("name")
        auth_status = st.session_state.get("authentication_status")

        if auth_status:
            st.sidebar.success(f"Bem-vindo, {name}")
            st.session_state["logged_in"] = True
            st.success("Login realizado com sucesso. Redirecionando...")
            st.switch_page("pages/1_Simulador.py")

        elif auth_status is False:
            st.session_state["logged_in"] = False
            st.error("Credenciais inválidas")
        elif auth_status is None:
            st.session_state["logged_in"] = False

    elif menu == "Cadastrar":
        st.title("📝 Cadastro de Novo Usuário")

        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        usuario = st.text_input("Usuário (login)")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
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

                    st.success(f"Usuário '{usuario}' cadastrado com sucesso!")

