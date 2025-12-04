SolarTrack v2.1 - Enterprise Solar Intelligence

Visão Geral

O SolarTrack é uma solução completa de Business Intelligence (BI) e monitoramento para gestão de ativos fotovoltaicos. Projetado com foco em UX Corporativa, o sistema abandona interfaces genéricas em favor de um design limpo, vetorial e orientado a dados.

Esta versão (v2.1 Enterprise) introduz uma arquitetura modular robusta, sistema de alertas em tempo real e relatórios financeiros detalhados (ROI, Payback, VPL).

Funcionalidades Principais

Interface & UX

Design Vetorial: Ícones SVG nítidos e identidade visual coesa (Azul/Laranja).

Navegação Intuitiva: Estrutura de sidebar limpa e navegação por cards.

Responsividade: Layout adaptável (wide mode) para grandes telas de monitoramento.

Módulos do Sistema

Simulador de Produção

Projeção energética baseada em irradiação e consumo.

Análise financeira automática (Economia mensal/anual).

Gestão de Acesso

Controle de usuários com hash seguro (SHA-256).

Painel administrativo para cadastro de equipe.

Business Intelligence (BI)

Dashboards interativos com Plotly.

Heatmaps de eficiência e curvas de carga.

Central de Monitoramento

Detecção de anomalias (Déficits críticos).

Log de incidentes auditável.

Exportação de Dados

Extração em múltiplos formatos: CSV, Excel, JSON e PDF.

Tratamento automático de metadados.

Configurações do Sistema

Ajustes globais de tema, idioma e SMTP (E-mail).

Logs de auditoria do sistema.

Arquitetura do Projeto

projeto_solar/
├── backend/                 # API e Lógica de Negócios
│   ├── main.py             # Ponto de entrada da API
│   ├── models.py           # Modelos de dados (Schemas)
│   └── auth.py             # Lógica de autenticação JWT
│
├── painel_admin/           # Frontend (Streamlit)
│   ├── Home.py             # Tela de Login e Dashboard Principal
│   ├── .streamlit/         # Configurações de tema e UI
│   │   └── config.toml
│   │
│   ├── pages/              # Módulos do Sistema
│   │   ├── 1_Simulador.py  # Ferramenta de Simulação
│   │   ├── 2_Cadastrar.py  # Gestão de Usuários
│   │   ├── 3_Relatorios.py # BI e Analytics
│   │   ├── 4_Exportacao.py # Central de Downloads
│   │   ├── 5_Alertas.py    # Monitoramento de Saúde
│   │   └── Ajustes.py      # Configurações Gerais
│   │
│   ├── shared.py           # Estilos CSS e funções globais
│   ├── alertas.py          # Lógica do sistema de alertas
│   ├── utils.py            # Utilitários de dados
│   ├── notificacoes.py     # Sistema de notificações
│   │
│   ├── usuarios.yaml       # Banco de dados local de usuários (Hash)
│   ├── configuracoes.json  # Preferências salvas
│   └── logs/               # Registros de atividade
│
└── requirements.txt        # Lista de dependências


Guia de Instalação

Pré-requisitos

Python 3.9 ou superior.

Git.

1. Clonar e Preparar

git clone [https://github.com/SeuUsuario/projeto_solar.git](https://github.com/SeuUsuario/projeto_solar.git)
cd projeto_solar

# Criar ambiente virtual (Recomendado)
python -m venv venv
# Ativar (Windows): venv\Scripts\activate
# Ativar (Linux/Mac): source venv/bin/activate


2. Instalar Dependências

pip install -r requirements.txt


3. Iniciar o Sistema

streamlit run painel_admin/Home.py


O painel será aberto em: http://localhost:8501

Credenciais Iniciais

Na primeira execução, se o arquivo usuarios.yaml não existir, você pode criar um usuário administrador através da aba "Solicitar Acesso" na tela de login.

Stack Tecnológica

Core: Python 3.10+

Frontend: Streamlit Framework

Analytics: Plotly Express & Graph Objects

Data Processing: Pandas / NumPy

Security: Streamlit-Authenticator

Reports: OpenPyXL (Excel) / FPDF (PDF)

© 2025 SolarTrack Systems. Desenvolvido para 