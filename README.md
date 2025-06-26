# Projeto: Painel Solar Interativo com Autenticação

Este projeto é uma aplicação web desenvolvida com a biblioteca Streamlit em Python. Ele simula a geração e o consumo de energia solar de forma visual e interativa. O sistema também oferece um mecanismo de autenticação de usuários (login e cadastro), controle de sessão e páginas separadas para simulação e configurações.
---
## Objetivo
O objetivo deste painel é permitir que o usuário simule o comportamento de um sistema de energia solar ao longo do dia, variando parâmetros como intensidade solar e consumo médio. Ele também permite a criação de novos usuários e a navegação segura com login e logout.
---
## Funcionalidades Principais
- Tela de login com autenticação de usuários via arquivo YAML
- Página de simulação com gráficos de produção, consumo e excedente de energia
- Página de cadastro para novos usuários
- Logout com encerramento completo da sessão
- Restrição de acesso às páginas apenas para usuários autenticados
- Proteção contra reentrada não autorizada
---

## Como Executar Localmente

### 1. Clone o repositório
```bash
git clone https://github.com/ArissonSilva13/projeto_solar.git
cd painel_admi

## Crie e ative um ambiente virtual
python -m venv venv 
venv\Scripts\activate

##  Instale as dependências
pip install -r requirements.txt

##Execute o sistema
streamlit run Home.py


Acesso de Teste
Usuário e senha padrão já cadastrados:

Usuário: admin
Senha: admin123
Você pode usar esse acesso inicial ou cadastrar novos usuários na opção "Cadastrar" do menu lateral.

Observações Técnicas
As senhas dos usuários são armazenadas de forma criptografada no arquivo usuarios.yaml.

O sistema usa st.session_state para controle de sessão e restrição de acesso.

A biblioteca streamlit_authenticator é usada para facilitar a autenticação.

O logout remove todas as chaves da sessão para garantir que o usuário seja desconectado completamente.

Requisitos
Python 3.9 ou superior

Streamlit

streamlit-authenticator

PyYAML

pandas

numpy

Esses pacotes estão listados no arquivo requirements.txt.