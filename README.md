# 🌞 Projeto Solar - Painel Interativo com Autenticação

## 📋 Descrição

Uma aplicação web desenvolvida com **Streamlit** e **FastAPI** que simula a geração e o consumo de energia solar de forma visual e interativa. O sistema oferece autenticação de usuários, controle de sessão e páginas separadas para simulação, relatórios avançados e configurações.

## 🎯 Objetivos

- Simular o comportamento de um sistema de energia solar ao longo do dia
- Permitir ajustes de parâmetros como intensidade solar e consumo médio
- Oferecer interface intuitiva para gerenciamento de usuários
- Proporcionar navegação segura com sistema de autenticação
- Gerar relatórios diversificados com visualizações interativas

## ⚡ Funcionalidades

### 🔐 Autenticação
- Sistema de login e logout seguro
- Cadastro de novos usuários
- Senhas criptografadas
- Controle de sessão com `st.session_state`

### 📊 Simulação
- Gráficos interativos de produção, consumo e excedente de energia
- Ajustes em tempo real dos parâmetros
- Visualização clara dos dados

### 📈 Relatórios Avançados
- **Resumo Geral**: Métricas principais com gráficos de linha e barras
- **Análise Detalhada**: Gráficos de área empilhada, análise de eficiência e produção por dia da semana
- **Comparativo Mensal**: Comparação entre meses e evolução da economia
- **Eficiência e Performance**: Gauge de eficiência e heatmap de produção
- **Exportação**: Dados em formato CSV e Excel
- **Período Personalizável**: Relatórios para 7, 30, 90 dias ou período customizado

### 🛡️ Segurança
- Restrição de acesso apenas para usuários autenticados
- Proteção contra reentrada não autorizada
- Logout completo com limpeza de sessão

## 🚀 Como Executar

### 📋 Pré-requisitos
- Python 3.9 ou superior
- Git

### 1️⃣ Clonar o Repositório
```bash
git clone https://github.com/ArissonSilva13/projeto_solar.git
cd projeto_solar
```

### 2️⃣ Configurar Ambiente Virtual (Único)

```bash
# Criar ambiente virtual na raiz do projeto
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instalar todas as dependências
pip install -r requirements.txt
```

### 3️⃣ Executar o Backend (API)

```bash
# Executar API (com ambiente virtual ativo)
cd backend
uvicorn main:app --reload
```

A API estará disponível em: `http://127.0.0.1:8000`

### 4️⃣ Executar o Frontend (Painel Admin)

**Em um novo terminal (com o mesmo ambiente virtual):**

```bash
# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Executar aplicação Streamlit
cd painel_admin
streamlit run Home.py
```

## 👤 Acesso de Teste

**Credenciais padrão:**
- **Usuário:** `admin`
- **Senha:** `admin123`

💡 **Dica:** Você pode usar essas credenciais iniciais ou cadastrar novos usuários através da opção "Cadastrar" no menu lateral.

## 🏗️ Estrutura do Projeto

```
projeto_solar/
├── backend/                 # API FastAPI
│   ├── main.py             # Aplicação principal
│   ├── models.py           # Modelos de dados
│   ├── database.py         # Configuração do banco
│   ├── auth.py             # Autenticação
│   └── requirements.txt    # Dependências do backend
├── painel_admin/           # Frontend Streamlit
│   ├── Home.py            # Página principal
│   ├── pages/             # Páginas da aplicação
│   │   ├── 1_Simulador.py # Simulação de energia
│   │   ├── 2_Configuracoes.py # Configurações
│   │   └── 3_Relatorios.py # Relatórios avançados
│   ├── shared.py          # Funções compartilhadas
│   ├── utils.py           # Utilitários para relatórios
│   ├── usuarios.yaml      # Dados dos usuários
│   └── requirements.txt   # Dependências do frontend
└── README.md              # Este arquivo
```

## 🔧 Tecnologias Utilizadas

### Frontend
- **Streamlit** - Framework web para Python
- **streamlit-authenticator** - Autenticação
- **PyYAML** - Manipulação de arquivos YAML
- **pandas** - Manipulação de dados
- **numpy** - Computação numérica
- **plotly** - Gráficos interativos avançados
- **openpyxl** - Exportação para Excel

### Backend
- **FastAPI** - Framework web moderno para APIs
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados

## 🔐 Observações Técnicas

- 🔒 **Segurança:** Senhas armazenadas de forma criptografada no arquivo `usuarios.yaml`
- 🎭 **Sessão:** Controle de sessão implementado com `st.session_state`
- 🚪 **Logout:** Remoção completa de todas as chaves da sessão
- 🛡️ **Restrições:** Acesso às páginas limitado apenas a usuários autenticados
- 🌐 **Ambiente Único:** Um único ambiente virtual é suficiente, pois não há conflitos entre dependências do frontend e backend
- 📊 **Relatórios:** Gráficos interativos com Plotly para melhor visualização dos dados

## 📦 Dependências

### Ambiente Único (`requirements.txt`)
```
# Backend (FastAPI + JWT + banco de dados)
fastapi
uvicorn[standard]
sqlalchemy
python-jose[cryptography]
passlib[bcrypt]

# Painel administrativo (Streamlit + autenticação)
streamlit
streamlit-authenticator
requests

# Simulador (dados e gráficos)
pandas
numpy
matplotlib
plotly  # Para gráficos interativos nos relatórios
kaleido  # Para exportação de gráficos plotly

# Dependências para funcionalidades de Ajustes
openpyxl  # Para exportação Excel
pyyaml    # Para manipulação de arquivos YAML
```

## 📊 Tipos de Relatórios Disponíveis

### 1. 📊 Resumo Geral
- Métricas principais de produção e consumo
- Gráficos de linha mostrando tendências
- Gráficos de barras para excedente diário
- Visão geral da performance do sistema

### 2. 🔍 Análise Detalhada
- Gráficos de área empilhada
- Análise de eficiência do sistema
- Produção média por dia da semana
- Scatter plot de performance

### 3. 📈 Comparativo Mensal
- Comparação entre meses
- Evolução da economia ao longo do tempo
- Tendências históricas
- Análise de crescimento

### 4. ⚡ Eficiência e Performance
- Gauge de eficiência em tempo real
- Heatmap de produção por semana e dia
- Análise de performance detalhada
- Indicadores de qualidade do sistema

### 💾 Funcionalidades de Exportação
- Exportação em CSV para análise externa
- Exportação em Excel com formatação
- Nomes de arquivo automáticos com data
- Compatibilidade com ferramentas de análise