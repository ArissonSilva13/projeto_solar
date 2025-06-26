# reset_admin.py

import yaml
from streamlit_authenticator import Hasher

# Dados do novo usuário
usuario = "admin"
senha = "admin123"
nome = "Administrador"
email = "admin@solar.com"

# Gera o hash da senha
senha_hash = Hasher([senha]).generate()[0]

# Estrutura correta do YAML
dados = {
    "usernames": {
        usuario: {
            "name": nome,
            "email": email,
            "password": senha_hash
        }
    }
}

# Salva no arquivo usuarios.yaml
with open("usuarios.yaml", "w") as f:
    yaml.dump(dados, f)

print(f"Usuário '{usuario}' recriado com sucesso!")
