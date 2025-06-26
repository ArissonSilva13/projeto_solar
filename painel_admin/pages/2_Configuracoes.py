import streamlit as st

# ✅ Proteção contra acesso indevido após logout
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

import yaml
import os
from streamlit_authenticator import Hasher

ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"

st.title(" Cadastro de Novo Usuário")

nome = st.text_input("Nome completo")
email = st.text_input("Email")
usuario = st.text_input("Usuário (login)")
senha = st.text_input("Senha", type="password")

if st.button("Cadastrar"):
    if not nome or not email or not usuario or not senha:
        st.warning("Por favor, preencha todos os campos.")
    else:
        # Carregar usuários existentes
        if os.path.exists(ARQUIVO_USUARIOS):
            with open(ARQUIVO_USUARIOS, "r") as f:
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

            with open(ARQUIVO_USUARIOS, "w") as f:
                yaml.dump(dados, f, default_flow_style=False)

            st.success(f"Usuário '{usuario}' cadastrado com sucesso!")
