import io
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

# Adiciona o diretório raiz para importações
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Importa estilo e utils
from shared import aplicar_estilo_solar

try:
    from painel_admin.utils import gerar_dados_relatorio, gerar_pdf_relatorio
except ImportError:
    try:
        from utils import gerar_dados_relatorio, gerar_pdf_relatorio
    except:
        # Mock para evitar crash se utils não estiver acessível
        def gerar_dados_relatorio(dias): return pd.DataFrame()
        def gerar_pdf_relatorio(df, g, r): return b""

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central de Exportação", page_icon="⚡", layout="wide")
aplicar_estilo_solar()

# --- VALIDAÇÃO DE LOGIN ---
if not st.session_state.get("logged_in"):
    st.error("🔒 Acesso restrito. Faça login.")
    st.stop()

# --- HELPER PARA ÍCONES SVG ---
def render_icon(svg_path, title, color="#1E3A8A"):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            {svg_path}
        </svg>
        <h4 style="margin: 0; color: #1E3A8A; font-weight: 600; font-family: sans-serif;">{title}</h4>
    </div>
    """, unsafe_allow_html=True)

st.title("Extração de Dados")
st.markdown("Download de relatórios técnicos e bases de dados para análise externa.")

# --- FUNÇÃO DE LIMPEZA DE DADOS ---
def padronizar_colunas_exportacao(df):
    """
    Garante que as colunas tenham nomes amigáveis para quem vai abrir o Excel/CSV.
    """
    if df is None or df.empty:
        return df
        
    col_map = {
        'producao_kwh': 'Gerado (kWh)',
        'consumo_kwh': 'Consumido (kWh)',
        'injetado_kwh': 'Excedente (kWh)',
        'economia_reais': 'Economia (R$)',
        'data': 'Data',
        'temperatura_media_c': 'Temperatura (°C)',
        'irradiancia_media_w_m2': 'Irradiação (W/m²)'
    }
    
    # Renomeia
    new_cols = []
    for col in df.columns:
        clean_col = str(col).lower().strip()
        new_cols.append(col_map.get(clean_col, col)) # Usa o nome bonito ou original
    
    df.columns = new_cols
    return df

# --- SIDEBAR: CONFIGURAÇÕES ---
with st.sidebar:
    st.header("Parâmetros de Extração")
    
    with st.form("form_exportacao"):
        # SVG: Calendar
        render_icon('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>', "Intervalo de Dados", "#FF8C00")
        
        periodo = st.selectbox(
            "Selecione o Período",
            ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Todo o Histórico"],
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # SVG: File Text
        render_icon('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>', "Opções de Relatório (PDF)", "#1E3A8A")
        
        incluir_graficos = st.checkbox("Incluir Gráficos Visuais", value=True)
        incluir_resumo = st.checkbox("Incluir KPIs e Estatísticas", value=True)
        
        st.markdown("---")
        
        # Botão de ação principal
        submitted = st.form_submit_button("Processar Dados", type="primary", use_container_width=True)

# --- LÓGICA DE CARREGAMENTO ---
if submitted:
    with st.spinner("Processando solicitação..."):
        # Determina dias baseado na seleção
        dias_map = {
            "Últimos 7 dias": 7,
            "Últimos 30 dias": 30,
            "Últimos 90 dias": 90,
            "Todo o Histórico": 3650
        }
        dias = dias_map.get(periodo, 30)
        
        # Busca dados
        df_raw = gerar_dados_relatorio(dias)
        
        # Limpa/Padroniza
        df_clean = padronizar_colunas_exportacao(df_raw)
        
        # Salva na sessão para persistir durante o download
        st.session_state.dados_exportacao = df_clean
        st.session_state.periodo_selecionado = periodo
        st.session_state.opcoes_pdf = {"graficos": incluir_graficos, "resumo": incluir_resumo}
        
        # Pequeno toast discreto em vez de mensagem grande
        st.toast("Dados prontos para download", icon="✅")

# --- ÁREA PRINCIPAL ---
if st.session_state.get("dados_exportacao") is not None:
    df = st.session_state.dados_exportacao
    
    st.markdown("---")
    
    # 1. KPIs do Arquivo (Feedback Visual)
    # SVG: Server/Database
    render_icon('<rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line>', "Resumo do Dataset")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Registros Encontrados", len(df))
        
        # Tenta mostrar totais se as colunas existirem
        if 'Gerado (kWh)' in df.columns:
            col2.metric("Volume Gerado", f"{df['Gerado (kWh)'].sum():.2f} kWh")
        if 'Economia (R$)' in df.columns:
            col3.metric("Valor Consolidado", f"R$ {df['Economia (R$)'].sum():.2f}")
            
        col4.metric("Intervalo Selecionado", st.session_state.get("periodo_selecionado", "-"))

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Abas de Ação
    tab_preview, tab_download = st.tabs(["Visualizar Tabela", "Opções de Download"])
    
    with tab_preview:
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            column_config={
                "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "Gerado (kWh)": st.column_config.NumberColumn(format="%.2f kWh"),
                "Consumido (kWh)": st.column_config.NumberColumn(format="%.2f kWh"),
                "Economia (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            }
        )
        st.caption(f"Exibindo amostra de {min(len(df), 1000)} registros.")

    with tab_download:
        st.markdown("##### Selecione o formato desejado:")
        
        c1, c2, c3, c4 = st.columns(4)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        with c1:
            # CSV
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar CSV",
                data=csv_data,
                file_name=f"solar_data_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
                type="secondary"
            )
            
        with c2:
            # EXCEL
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Dados Solar")
            
            st.download_button(
                label="Baixar Excel",
                data=buffer.getvalue(),
                file_name=f"solar_report_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="secondary"
            )
            
        with c3:
            # JSON
            json_data = df.to_json(orient="records", indent=2)
            st.download_button(
                label="Baixar JSON",
                data=json_data,
                file_name=f"solar_data_{timestamp}.json",
                mime="application/json",
                use_container_width=True,
                type="secondary"
            )

        with c4:
            # PDF
            opts = st.session_state.get("opcoes_pdf", {"graficos": True, "resumo": True})
            
            if st.button("Gerar PDF", use_container_width=True, type="primary"):
                with st.spinner("Gerando documento..."):
                    try:
                        pdf_bytes = gerar_pdf_relatorio(df, opts["graficos"], opts["resumo"])
                        st.download_button(
                            label="Salvar PDF",
                            data=pdf_bytes,
                            file_name=f"relatorio_oficial_{timestamp}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="btn_pdf_download"
                        )
                    except Exception as e:
                        st.error(f"Erro na geração do PDF: {str(e)}")

else:
    # Estado inicial clean (Placeholder)
    st.info("Configure os filtros na barra lateral para carregar os dados.")
    
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown(
            """
            <div style="text-align: center; color: #cbd5e1; padding: 60px; border: 2px dashed #e2e8f0; border-radius: 12px; margin-top: 20px;">
                <h2 style="margin:0;">📥</h2>
                <p style="margin-top:10px;">Nenhum dado carregado.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )