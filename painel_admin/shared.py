import streamlit as st
import streamlit_authenticator as stauth
import yaml
import os

def aplicar_estilo_solar():
    """
    Função para injetar CSS personalizado.
    Deve ser chamada logo após st.set_page_config() em todas as páginas.
    """
    st.markdown("""
        <style>
        /* --- 1. MELHORIA DOS CARDS DE MÉTRICAS --- */
        div[data-testid="metric-container"] {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        div[data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            border-color: #FF8C00;
        }

        /* --- 2. TÍTULOS --- */
        h1 {
            color: #1E3A8A; 
            font-weight: 700;
            padding-bottom: 10px;
        }

        /* --- 3. BOTÕES --- */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: all 0.2s;
        }
        
        /* --- 4. LIMPEZA VISUAL --- */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

def carregar_autenticador():
    # --- CORREÇÃO DO CAMINHO (ABSOLUTO DINÂMICO) ---
    # 1. Descobre onde o arquivo 'shared.py' está salvo
    diretorio_atual = os.path.dirname(__file__)
    
    # 2. Monta o caminho para o usuarios.yaml na mesma pasta
    caminho_arquivo = os.path.join(diretorio_atual, "usuarios.yaml")
    
    # 3. Tenta carregar. Se falhar, tenta o caminho local de desenvolvimento como fallback
    if not os.path.exists(caminho_arquivo):
        # Fallback para execução local simples se necessário
        caminho_arquivo = "painel_admin/usuarios.yaml"
    
    with open(caminho_arquivo) as file:
        credentials = yaml.safe_load(file)

    authenticator = stauth.Authenticate(
        credentials,
        "monitoramento_solar",
        "abc123",
        cookie_expiry_days=1
    )
    return authenticator