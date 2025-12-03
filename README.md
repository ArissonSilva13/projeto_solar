SolarTrack - Sistema de Gestão de Energia Fotovoltaica

Descrição do Projeto

O SolarTrack é uma plataforma de Business Intelligence (BI) e monitoramento para sistemas de energia solar. Desenvolvida em Python utilizando Streamlit para o frontend e FastAPI para o backend, a aplicação oferece uma interface profissional para simulação de geração de energia, análise financeira (ROI), monitoramento de alertas em tempo real e gestão de usuários.

O sistema foi projetado para oferecer uma experiência de "SaaS" (Software as a Service), com painéis interativos, gráficos dinâmicos (Plotly) e exportação de dados em múltiplos formatos.

Funcionalidades Principais

1. Autenticação e Segurança

Sistema de login seguro com hash de senhas.

Gestão de sessão persistente.

Controle de acesso (apenas usuários autenticados acessam o painel).

Interface de login moderna com identidade visual corporativa.

2. Simulador Solar

Projeção de geração de energia baseada em intensidade solar e consumo.

Cálculo financeiro automático: Economia diária, mensal e anual.

Estimativa de Payback (Tempo de Retorno) e ROI em 25 anos.

Visualização gráfica da curva de produção x consumo.

3. Relatórios e BI

Dashboard interativo com filtros de período (7, 30, 90 dias ou personalizado).

Análise de eficiência do sistema.

Mapas de calor (Heatmap) para identificar horários de pico.

Comparativos mensais e anuais.

4. Central de Monitoramento (Alertas)

Detecção automática de anomalias (Déficit de produção, falhas de inversor).

Classificação de incidentes por severidade (Crítico, Moderado, Informativo).

Recomendações automáticas baseadas no tipo de alerta.

Histórico completo de incidentes.

5. Gestão de Dados (Exportação)

Pré-visualização de dados antes do download.

Suporte a múltiplos formatos: CSV, Excel (XLSX), JSON e PDF.

Padronização automática de colunas para facilitar a leitura externa.

Estrutura do Projeto

projeto_solar/
├── backend/                 # API e Lógica de Negócios
│   ├── main.py             # Ponto de entrada da API
│   ├── models.py           # Modelos de dados (Schemas)
│   └── auth.py             # Lógica de autenticação JWT
├── painel_admin/           # Frontend (Streamlit)
│   ├── Home.py             # Tela de Login e Dashboard Principal
│   ├── .streamlit/         # Configurações de tema e UI
│   ├── pages/              # Módulos do Sistema
│   │   ├── 1_Simulador.py  # Ferramenta de Simulação
│   │   ├── 2_Cadastrar.py  # Gestão de Usuários
│   │   ├── 3_Relatorios.py # BI e Analytics
│   │   ├── 4_Exportacao.py # Central de Downloads
│   │   └── 5_Alertas.py    # Monitoramento de Saúde
│   ├── shared.py           # Estilos CSS e funções globais
│   ├── alertas.py          # Lógica do sistema de alertas
│   └── usuarios.yaml       # Banco de dados local de usuários (Hash)
└── requirements.txt        # Lista de dependências


Guia de Instalação e Execução

Siga os passos abaixo para rodar o projeto em sua máquina local.

Pré-requisitos

Python 3.9 ou superior instalado.

Git instalado.

1. Clonar o Repositório

Abra seu terminal ou CMD e execute:

git clone [https://github.com/ArissonSilva13/projeto_solar.git](https://github.com/ArissonSilva13/projeto_solar.git)
cd projeto_solar


2. Configurar o Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências.

Windows:

python -m venv venv
venv\Scripts\activate


Linux/macOS:

python3 -m venv venv
source venv/bin/activate


3. Instalar Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

pip install -r requirements.txt


4. Executar a Aplicação

Para iniciar o painel administrativo (Frontend):

streamlit run painel_admin/Home.py


O sistema abrirá automaticamente no seu navegador no endereço: http://localhost:8501

Credenciais de Acesso

Para o primeiro acesso, utilize as credenciais de administrador padrão (caso configuradas) ou edite o arquivo painel_admin/usuarios.yaml seguindo o modelo de hash.

Se o arquivo de usuários não existir, o sistema criará um novo automaticamente na primeira execução ou permitirá o cadastro via código inicial.

Tecnologias Utilizadas

Linguagem: Python 3.10+

Frontend: Streamlit

Visualização de Dados: Plotly Express / Graph Objects

Manipulação de Dados: Pandas / NumPy

Autenticação: Streamlit-Authenticator

Exportação: OpenPyXL (Excel), FPDF (PDF)

Contribuição

Faça um Fork do projeto.

Crie uma Branch para sua Feature (git checkout -b feature/NovaFeature).

Faça o Commit (git commit -m 'Add: Nova Feature').

Faça o Push (git push origin feature/NovaFeature).

Abra um Pull Request.

Desenvolvido por Arisson Silva
