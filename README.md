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
- Análise de performance em tempo real

### 📈 Relatórios Avançados
- **Resumo Geral**: Métricas principais com gráficos de linha e barras
- **Análise Detalhada**: Gráficos de área empilhada, análise de eficiência e produção por dia da semana
- **Comparativo Mensal**: Comparação entre meses e evolução da economia
- **Eficiência e Performance**: Gauge de eficiência e heatmap de produção
- **Período Personalizável**: Relatórios para 7, 30, 90 dias ou período customizado
- **Métricas Avançadas**: Cálculos de eficiência, melhor/pior dia, percentual de excedente

### 📥 Exportação de Dados
- **Múltiplos Formatos**: CSV, Excel, JSON e PDF
- **Relatórios Personalizados**: Escolha períodos específicos
- **Gráficos Inclusos**: Visualizações em relatórios PDF
- **Dados Históricos**: Exportação completa de dados históricos
- **Configurações Flexíveis**: Opção de incluir/excluir gráficos e resumos estatísticos

### 🚨 Sistema de Alertas
- **Monitoramento Inteligente**: Alertas automáticos baseados em thresholds configuráveis
- **Níveis de Alerta**: Crítico, moderado e atenção
- **Notificações por Email**: Sistema completo de notificações SMTP
- **Análise de Déficits**: Detecção de déficits críticos e moderados
- **Recomendações Automáticas**: Sugestões de otimização baseadas nos alertas
- **Exportação de Alertas**: Histórico completo de alertas em formato planilha

### 👤 Gerenciamento de Usuários
- **Cadastro Simplificado**: Interface intuitiva para cadastro
- **Validação de Dados**: Verificação de campos obrigatórios
- **Gestão de Perfis**: Armazenamento seguro de dados de usuários
- **Controle de Acesso**: Sistema de permissões por usuário

### 🛡️ Segurança
- Restrição de acesso apenas para usuários autenticados
- Proteção contra reentrada não autorizada
- Logout completo com limpeza de sessão
- Criptografia de senhas com hash seguro

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

A aplicação estará disponível em: `http://localhost:8501`

## 🧭 Navegação do Sistema

### 📱 Páginas Principais
1. **🏠 Home** - Visão geral do sistema e navegação rápida
2. **🔋 Simulador** - Simulação interativa de energia solar
3. **👤 Cadastrar Usuário** - Gerenciamento de usuários do sistema
4. **📊 Relatórios** - Relatórios avançados e análises detalhadas
5. **📥 Exportação** - Exportação de dados em múltiplos formatos
6. **🚨 Alertas** - Sistema de monitoramento e alertas inteligentes
7. **🛠️ Ajustes** - Configurações administrativas e backup

### 🔧 Menu Lateral
- **Login/Logout** - Controle de acesso ao sistema
- **Navegação Rápida** - Acesso direto a todas as funcionalidades
- **Status do Usuário** - Informações da sessão atual

## 👤 Acesso de Teste

**Credenciais padrão:**
- **Usuário:** `admin`
- **Senha:** `admin123`

💡 **Dica:** Você pode usar essas credenciais iniciais ou cadastrar novos usuários através da página "Cadastrar Usuário" no menu lateral.

## 🏗️ Estrutura do Projeto

```
projeto_solar/
├── backend/                 # API FastAPI
│   ├── main.py             # Aplicação principal
│   ├── models.py           # Modelos de dados
│   ├── database.py         # Configuração do banco
│   └── auth.py             # Autenticação
├── painel_admin/           # Frontend Streamlit
│   ├── Home.py            # Página principal
│   ├── pages/             # Páginas da aplicação
│   │   ├── 1_Simulador.py # Simulação de energia
│   │   ├── 2_Cadastrar_Usuario.py # Cadastro de usuários
│   │   ├── 3_Relatorios.py # Relatórios avançados
│   │   ├── 4_Exportacao.py # Exportação de dados
│   │   ├── 5_Alertas.py   # Sistema de alertas
│   │   └── Ajustes.py     # Configurações administrativas
│   ├── shared.py          # Funções compartilhadas
│   ├── utils.py           # Utilitários para relatórios
│   ├── alertas.py         # Sistema de alertas
│   ├── email_utils.py     # Utilitários para email
│   ├── notificacoes.py    # Sistema de notificações
│   ├── usuarios.yaml      # Dados dos usuários
│   ├── painel_admin/      # Configurações do sistema
│   │   ├── configuracoes.json # Configurações gerais
│   │   └── logs/          # Logs do sistema
│   └── reset_admin.py     # Utilitário para reset de admin
├── requirements.txt       # Dependências do projeto
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
- **fpdf** - Geração de relatórios PDF
- **matplotlib** - Gráficos para relatórios PDF

### Backend
- **FastAPI** - Framework web moderno para APIs
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados

### Sistema de Alertas
- **SMTP** - Envio de emails para notificações
- **JSON** - Configurações do sistema
- **logging** - Sistema de logs

## 🔐 Observações Técnicas

- 🔒 **Segurança:** Senhas armazenadas de forma criptografada no arquivo `usuarios.yaml`
- 🎭 **Sessão:** Controle de sessão implementado com `st.session_state`
- 🚪 **Logout:** Remoção completa de todas as chaves da sessão
- 🛡️ **Restrições:** Acesso às páginas limitado apenas a usuários autenticados
- 🌐 **Ambiente Único:** Um único ambiente virtual é suficiente, pois não há conflitos entre dependências
- 📊 **Relatórios:** Gráficos interativos com Plotly e exportação em múltiplos formatos
- 🚨 **Alertas:** Sistema inteligente de monitoramento com notificações por email
- 📥 **Exportação:** Suporte completo para CSV, Excel, JSON e PDF com gráficos inclusos
- 📧 **Email:** Sistema SMTP configurável para notificações automáticas
- 🔧 **Configurações:** Arquivos JSON para configurações centralizadas do sistema
- 📝 **Logs:** Sistema de logging para rastreamento de atividades

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

# Sistema de Exportação
openpyxl  # Para exportação Excel
fpdf      # Para geração de relatórios PDF

# Sistema de Alertas e Notificações
pyyaml    # Para manipulação de arquivos YAML
smtplib   # Para envio de emails (built-in)
email     # Para formatação de emails (built-in)

# Configurações e utilitários
json      # Para configurações (built-in)
logging   # Para sistema de logs (built-in)
io        # Para manipulação de arquivos (built-in)
datetime  # Para datas e horários (built-in)
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

## 📥 Sistema de Exportação

### 💾 Formatos Disponíveis
- **CSV**: Dados em formato tabular para análise externa
- **Excel**: Planilhas formatadas com múltiplas abas
- **JSON**: Dados estruturados para integração com outros sistemas
- **PDF**: Relatórios completos com gráficos e análises

### 🔧 Funcionalidades de Exportação
- **Períodos Personalizáveis**: Escolha de datas específicas
- **Configurações Flexíveis**: Opção de incluir/excluir gráficos
- **Nomes Automáticos**: Arquivos com timestamp automático
- **Resumos Estatísticos**: Métricas calculadas automaticamente

## 🚨 Sistema de Alertas

### 📋 Tipos de Alertas
- **Críticos**: Déficits energéticos severos (⚠️ vermelho)
- **Moderados**: Déficits energéticos leves (⚠️ amarelo)
- **Atenção**: Situações que requerem monitoramento (ℹ️ azul)

### 📧 Notificações por Email
- **Configuração SMTP**: Suporte completo para servidores de email
- **Templates HTML**: Emails formatados profissionalmente
- **Anexos**: Possibilidade de incluir relatórios nos emails
- **Testes de Configuração**: Verificação automática das configurações

### 🔍 Análise Inteligente
- **Thresholds Configuráveis**: Limites personalizáveis para cada tipo de alerta
- **Análise de Tendências**: Identificação de padrões problemáticos
- **Recomendações Automáticas**: Sugestões baseadas nos dados
- **Histórico de Alertas**: Registro completo para análise posterior