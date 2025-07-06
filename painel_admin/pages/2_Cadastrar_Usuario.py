import streamlit as st

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

import yaml
import os
from streamlit_authenticator import Hasher
from notificacoes import NotificacaoRealTime

ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"

st.title("👤 Cadastrar Usuário")
st.info("⚠️ Esta tela é exclusiva para administradores do sistema")

notificacao_system = NotificacaoRealTime()

def verificar_alertas_sistema():
    if not os.path.exists(ARQUIVO_USUARIOS):
        notificacao_system.adicionar_notificacao(
            'sistema',
            'Arquivo de Usuários Não Encontrado',
            'O arquivo de usuários não foi encontrado. Será criado automaticamente.',
            'baixa'
        )
    
    try:
        with open(ARQUIVO_USUARIOS, "r") as f:
            dados = yaml.safe_load(f) or {}
        
        num_usuarios = len(dados.get("usernames", {}))
        
        if num_usuarios == 0:
            notificacao_system.adicionar_notificacao(
                'sistema',
                'Nenhum Usuário Cadastrado',
                'Sistema sem usuários cadastrados. Recomenda-se criar pelo menos um usuário.',
                'media'
            )
        elif num_usuarios > 10:
            notificacao_system.adicionar_notificacao(
                'sistema',
                'Muitos Usuários',
                f'{num_usuarios} usuários cadastrados. Considere revisar permissões.',
                'baixa'
            )
    except Exception as e:
        notificacao_system.adicionar_notificacao(
            'sistema',
            'Erro ao Ler Arquivo',
            f'Erro ao verificar arquivo de usuários: {str(e)}',
            'alta'
        )

verificar_alertas_sistema()

nome = st.text_input("Nome completo")
email = st.text_input("Email")
usuario = st.text_input("Usuário (login)")
senha = st.text_input("Senha", type="password")

if st.button("Cadastrar"):
    if not nome or not email or not usuario or not senha:
        st.warning("Por favor, preencha todos os campos.")
    else:
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
            
            notificacao_system.adicionar_notificacao(
                'usuario_criado',
                'Usuário Cadastrado',
                f'Usuário "{usuario}" foi cadastrado com sucesso no sistema.',
                'baixa'
            )

st.sidebar.divider()
notificacao_system.exibir_painel_notificacoes()
notificacao_system.auto_refresh_alertas()

notificacao_system.limpar_notificacoes_antigas()
