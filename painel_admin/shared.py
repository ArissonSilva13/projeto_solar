import yaml
import streamlit_authenticator as stauth

def carregar_autenticador():
    with open("usuarios.yaml") as file:
        credentials = yaml.safe_load(file)

    authenticator = stauth.Authenticate(
        credentials,
        "monitoramento_solar",
        "abc123",
        cookie_expiry_days=1
    )
    return authenticator


