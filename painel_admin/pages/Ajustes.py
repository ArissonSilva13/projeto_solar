import streamlit as st

# ✅ Proteção de acesso
if not st.session_state.get("logged_in"):
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

st.title(" Configurações")
st.write("Em breve: opções de usuário, relatórios, exportação e integração.")