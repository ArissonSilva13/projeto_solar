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
    # Fallback para desenvolvimento local caso utils não seja encontrado
    from utils import gerar_dados_relatorio, gerar_pdf_relatorio

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central de Exportação", page_icon="📥", layout="wide")
aplicar_estilo_solar() # Aplica o visual "Solar Tech"

# --- VALIDAÇÃO DE LOGIN ---
if not st.session_state.get("logged_in"):
    st.warning("🔒 Acesso restrito. Por favor, faça login.")
    st.stop()

st.title("📥 Central de Exportação de Dados")
st.markdown("Extraia dados brutos ou relatórios formatados para análise externa.")

# --- FUNÇÃO DE LIMPEZA DE DADOS (Igual à de Relatórios) ---
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
    st.header("⚙️ Filtros de Extração")
    
    with st.form("form_exportacao"):
        periodo = st.selectbox(
            "📅 Período dos Dados",
            ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Todo o Histórico"]
        )
        
        st.markdown("### Opções do Relatório PDF")
        incluir_graficos = st.checkbox("Incluir Gráficos Visuais", value=True)
        incluir_resumo = st.checkbox("Incluir KPIs e Estatísticas", value=True)
        
        st.divider()
        
        # Botão de ação principal dentro do form
        submitted = st.form_submit_button("🔍 Carregar Pré-visualização", type="primary", use_container_width=True)

# --- LÓGICA DE CARREGAMENTO ---
if submitted:
    with st.spinner("Buscando e processando dados..."):
        # Determina dias baseado na seleção
        dias_map = {
            "Últimos 7 dias": 7,
            "Últimos 30 dias": 30,
            "Últimos 90 dias": 90,
            "Todo o Histórico": 3650 # 10 anos
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
        
        st.toast("Dados carregados com sucesso!", icon="✅")

# --- ÁREA PRINCIPAL ---
if st.session_state.get("dados_exportacao") is not None:
    df = st.session_state.dados_exportacao
    
    # 1. KPIs do Arquivo (Feedback Visual)
    st.markdown("### 📋 Resumo do Arquivo")
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Linhas (Registros)", len(df))
        
        # Tenta mostrar totais se as colunas existirem
        if 'Gerado (kWh)' in df.columns:
            col2.metric("Total Gerado", f"{df['Gerado (kWh)'].sum():.2f} kWh")
        if 'Economia (R$)' in df.columns:
            col3.metric("Valor Total", f"R$ {df['Economia (R$)'].sum():.2f}")
            
        col4.metric("Período", st.session_state.get("periodo_selecionado", "-"))

    # 2. Abas de Ação
    tab_preview, tab_download = st.tabs(["👁️ Pré-visualização da Tabela", "💾 Central de Download"])
    
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
        st.caption(f"Mostrando as primeiras {min(len(df), 1000)} linhas de {len(df)} totais.")

    with tab_download:
        st.markdown("#### Selecione o formato para baixar:")
        
        c1, c2, c3, c4 = st.columns(4)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        with c1:
            # CSV
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Baixar CSV",
                data=csv_data,
                file_name=f"solar_data_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Formato leve, ideal para importar em outros sistemas."
            )
            
        with c2:
            # EXCEL
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Dados Solar")
            
            st.download_button(
                label="📊 Baixar Excel",
                data=buffer.getvalue(),
                file_name=f"solar_report_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Melhor opção para editar e criar gráficos no Office."
            )
            
        with c3:
            # JSON
            json_data = df.to_json(orient="records", indent=2)
            st.download_button(
                label="code Baixar JSON",
                data=json_data,
                file_name=f"solar_data_{timestamp}.json",
                mime="application/json",
                use_container_width=True,
                help="Para desenvolvedores e integrações via API."
            )

        with c4:
            # PDF
            # Verifica opções salvas
            opts = st.session_state.get("opcoes_pdf", {"graficos": True, "resumo": True})
            
            # Botão que gera o PDF sob demanda (pode demorar um pouco mais)
            if st.button("📑 Gerar PDF", use_container_width=True, type="primary"):
                with st.spinner("Gerando documento PDF..."):
                    try:
                        pdf_bytes = gerar_pdf_relatorio(df, opts["graficos"], opts["resumo"])
                        st.download_button(
                            label="⬇️ Clique para Salvar PDF",
                            data=pdf_bytes,
                            file_name=f"relatorio_oficial_{timestamp}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="btn_pdf_download" # Key única para não recarregar
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar PDF: {str(e)}")
                        st.info("Verifique se as bibliotecas 'fpdf' ou 'reportlab' estão instaladas.")

else:
    # Estado inicial vazio
    st.info("👈 Utilize a barra lateral para selecionar o período e carregar os dados.")
    
    # Ilustração visual vazia
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown(
            """
            <div style="text-align: center; color: #aaa; padding: 50px; border: 2px dashed #ddd; border-radius: 10px;">
                <h3>📤 Pronto para Exportar</h3>
                <p>Selecione os filtros ao lado para começar.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )