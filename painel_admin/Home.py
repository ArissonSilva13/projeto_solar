import streamlit as st
from shared import carregar_autenticador
import streamlit_authenticator as stauth
import yaml, os
from streamlit_authenticator import Hasher

st.set_page_config(page_title="Início", page_icon="☀️", layout="centered", initial_sidebar_state="collapsed")

# ✅ Garante que 'logged_in' esteja sempre definido
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 🔁 Função para logout completo e seguro
def realizar_logout():
    for chave in list(st.session_state.keys()):
        del st.session_state[chave]
    st.rerun()

# ✅ Verifica se está logado
if st.session_state.get("logged_in"):
    st.title("☀️ Painel Solar - Sistema de Monitoramento e Simulação")

    # 🎯 Introdução Principal
    st.markdown("""
    ## 🌞 Bem-vindo ao Sistema de Energia Solar Inteligente

    Uma plataforma completa e interativa para **monitoramento, simulação e análise de produção de energia solar**. 
    Desenvolvido com tecnologias modernas para oferecer uma experiência intuitiva e dados precisos sobre 
    o desempenho do seu sistema fotovoltaico.
    """)

    # 📊 Seção de Funcionalidades
    st.markdown("---")
    st.subheader("🚀 Funcionalidades Principais")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🔋 Simulação Avançada
        - **Produção em tempo real**: Simule a geração de energia ao longo do dia
        - **Consumo inteligente**: Monitore o consumo de energia da sua residência
        - **Análise de excedentes**: Visualize quando há sobra de energia
        - **Parâmetros ajustáveis**: Configure intensidade solar e consumo médio

        ### 📈 Relatórios Detalhados
        - **Resumo geral**: Métricas principais com gráficos interativos
        - **Análise detalhada**: Gráficos de área empilhada e eficiência
        - **Comparativo mensal**: Evolução da economia ao longo do tempo
        - **Performance**: Gauge de eficiência e heatmap de produção
        """)

    with col2:
        st.markdown("""
        ### ⚙️ Configurações Flexíveis
        - **Parâmetros customizáveis**: Ajuste todos os aspectos da simulação
        - **Perfis de consumo**: Defina diferentes padrões de uso
        - **Configurações de sistema**: Personalize painéis e inversores
        - **Backup e restauração**: Salve e carregue configurações

        ### 💾 Exportação de Dados
        - **Formato CSV**: Para análise em planilhas
        - **Formato Excel**: Com formatação profissional
        - **Relatórios PDF**: Documentos para apresentações
        - **Dados históricos**: Acesso a informações passadas
        """)

    # 🎯 Benefícios
    st.markdown("---")
    st.subheader("💡 Benefícios do Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 🌱 Sustentabilidade
        - Redução da pegada de carbono
        - Uso eficiente de energia renovável
        - Monitoramento do impacto ambiental
        - Otimização do consumo
        """)

    with col2:
        st.markdown("""
        #### 💰 Economia
        - Redução na conta de energia
        - Análise de retorno do investimento
        - Identificação de oportunidades
        - Planejamento financeiro
        """)

    with col3:
        st.markdown("""
        #### 📊 Inteligência
        - Dados em tempo real
        - Análises preditivas
        - Relatórios automáticos
        - Tomada de decisão informada
        """)

    # 🛠️ Como Usar
    st.markdown("---")
    st.subheader("🗺️ Como Utilizar o Sistema")

    with st.expander("🔋 Simulador de Energia", expanded=False):
        st.markdown("""
        **Acesse o simulador para:**
        - Visualizar gráficos de produção, consumo e excedente
        - Ajustar parâmetros como intensidade solar e consumo
        - Acompanhar métricas em tempo real
        - Analisar o desempenho do sistema
        
        **Dica**: Use os controles deslizantes para ver como diferentes condições afetam a produção.
        """)

    with st.expander("📊 Relatórios Avançados", expanded=False):
        st.markdown("""
        **Tipos de relatórios disponíveis:**
        - **Resumo Geral**: Visão geral da performance
        - **Análise Detalhada**: Gráficos avançados e métricas
        - **Comparativo Mensal**: Evolução ao longo do tempo
        - **Eficiência**: Indicadores de performance
        
        **Funcionalidades**: Exportação em CSV/Excel e períodos personalizáveis (7, 30, 90 dias).
        """)

    with st.expander("⚙️ Configurações", expanded=False):
        st.markdown("""
        **Personalize seu sistema:**
        - Defina parâmetros de geração solar
        - Configure perfis de consumo
        - Ajuste configurações de equipamentos
        - Defina alertas e notificações
        
        **Importante**: Salve suas configurações para manter as personalizações.
        """)

    with st.expander("🛠️ Ajustes Avançados", expanded=False):
        st.markdown("""
        **Funcionalidades administrativas:**
        - Backup e restauração de dados
        - Configurações de sistema
        - Gerenciamento de usuários
        - Manutenção de dados
        
        **Acesso**: Disponível para administradores do sistema.
        """)

    # 🔧 Tecnologias
    st.markdown("---")
    st.subheader("🔧 Tecnologias Utilizadas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### Frontend
        - **Streamlit**: Interface web interativa
        - **Plotly**: Gráficos avançados e interativos
        - **Pandas**: Manipulação de dados
        - **NumPy**: Computação numérica
        """)

    with col2:
        st.markdown("""
        #### Backend
        - **FastAPI**: API REST moderna
        - **SQLAlchemy**: ORM para banco de dados
        - **Python**: Linguagem principal
        - **YAML**: Configurações e autenticação
        """)

    # 📞 Suporte
    st.markdown("---")
    st.subheader("📞 Suporte e Ajuda")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **🆘 Precisa de ajuda?**
        - Consulte a documentação em cada página
        - Use as dicas interativas nos controles
        - Verifique os exemplos nos relatórios
        """)

    with col2:
        st.success("""
        **✅ Dicas para melhor uso:**
        - Mantenha suas configurações sempre atualizadas
        - Exporte dados regularmente para backup
        - Monitore os relatórios periodicamente
        """)

    # 🚀 Navegação
    st.markdown("---")
    st.subheader("🚀 Navegação Rápida")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔋 Ir para Simulador", use_container_width=True):
            st.switch_page("pages/1_Simulador.py")

    with col2:
        if st.button("📊 Ver Relatórios", use_container_width=True):
            st.switch_page("pages/3_Relatorios.py")

    with col3:
        if st.button("⚙️ Configurações", use_container_width=True):
            st.switch_page("pages/2_Configuracoes.py")

    # Sidebar
    st.sidebar.success("Você está logado.")
    st.sidebar.markdown("### 🧭 Navegação")
    st.sidebar.page_link("pages/1_Simulador.py", label="🔋 Simulador")
    st.sidebar.page_link("pages/2_Configuracoes.py", label="⚙️ Configurações")
    st.sidebar.page_link("pages/3_Relatorios.py", label="📊 Relatórios")
    st.sidebar.page_link("pages/Ajustes.py", label="🛠️ Ajustes")

    st.sidebar.markdown("---")
    if st.sidebar.button("🔓 Logout"):
        realizar_logout()

else:
    menu = st.sidebar.radio("Menu", ["Login", "Cadastrar"])

    if menu == "Login":
        st.title("🔐 Login")
        authenticator = carregar_autenticador()

        authenticator.login(fields={'Form name': 'Login', 'Username': 'Usuário', 'Password': 'Senha'})

        name = st.session_state.get("name")
        auth_status = st.session_state.get("authentication_status")

        if auth_status:
            st.sidebar.success(f"Bem-vindo, {name}")
            st.session_state["logged_in"] = True
            st.success("Login realizado com sucesso. Redirecionando...")
            st.switch_page("pages/1_Simulador.py")

        elif auth_status is False:
            st.session_state["logged_in"] = False
            st.error("Credenciais inválidas")
        elif auth_status is None:
            st.session_state["logged_in"] = False

    elif menu == "Cadastrar":
        st.title("📝 Cadastro de Novo Usuário")

        nome = st.text_input("Nome completo")
        email = st.text_input("Email")
        usuario = st.text_input("Usuário (login)")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            ARQUIVO = "painel_admin/usuarios.yaml"

            if not nome or not email or not usuario or not senha:
                st.warning("Preencha todos os campos.")
            else:
                if os.path.exists(ARQUIVO):
                    with open(ARQUIVO, "r") as f:
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

                    with open(ARQUIVO, "w") as f:
                        yaml.dump(dados, f)

                    st.success(f"Usuário '{usuario}' cadastrado com sucesso!")

