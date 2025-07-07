import yaml
from streamlit_authenticator import Hasher

usuario = "admin"
senha = "admin123"
nome = "Administrador"
email = "admin@solar.com"

senha_hash = Hasher([senha]).generate()[0]

dados = {
    "usernames": {
        usuario: {
            "name": nome,
            "email": email,
            "password": senha_hash
        }
    }
}

with open("usuarios.yaml", "w") as f:
    yaml.dump(dados, f)

print(f"Usuário '{usuario}' recriado com sucesso!")
