import io
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from painel_admin.utils import gerar_dados_relatorio, gerar_pdf_relatorio

if not st.session_state.get("logged_in"):
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

st.set_page_config(page_title="Exportação", page_icon="📥", layout="wide")

st.title("📥 Exportação de Dados")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Configurações de Exportação")

    formato_exportacao = st.selectbox(
        "Formato de Arquivo", ["CSV", "Excel (XLSX)", "JSON", "PDF (Relatório)"]
    )

    periodo_exportacao = st.selectbox(
        "Período para Exportação",
        ["Últimos 7 dias", "Últimos 30 dias", "Todos os dados"],
    )

    incluir_graficos = st.checkbox("Incluir gráficos (apenas PDF)", value=True)
    incluir_resumo = st.checkbox("Incluir resumo estatístico", value=True)

    if st.button("📥 Preparar Exportação"):
        if periodo_exportacao == "Últimos 7 dias":
            df_export = gerar_dados_relatorio(7)
        elif periodo_exportacao == "Últimos 30 dias":
            df_export = gerar_dados_relatorio(30)
        else:
            df_export = gerar_dados_relatorio(90)

        st.session_state.dados_exportacao = df_export
        st.session_state.formato_export = formato_exportacao
        st.session_state.incluir_graficos = incluir_graficos
        st.session_state.incluir_resumo = incluir_resumo
        st.success("Dados preparados para exportação!")

with col2:
    st.subheader("Download de Arquivos")

    if st.session_state.get("dados_exportacao") is not None:
        df_export = st.session_state.dados_exportacao
        formato = st.session_state.get("formato_export", "CSV")

        if formato == "CSV":
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        elif formato == "Excel (XLSX)":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="Dados")

            st.download_button(
                label="💾 Download Excel",
                data=buffer.getvalue(),
                file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        elif formato == "JSON":
            json_data = df_export.to_json(orient="records", indent=2)
            st.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
            )

        elif formato == "PDF (Relatório)":
            incluir_graficos = st.session_state.get("incluir_graficos", True)
            incluir_resumo = st.session_state.get("incluir_resumo", True)

            pdf_data = gerar_pdf_relatorio(df_export, incluir_graficos, incluir_resumo)

            st.download_button(
                label="💾 Download PDF",
                data=pdf_data,
                file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

        st.subheader("Pré-visualização")
        st.dataframe(df_export.head(), use_container_width=True) 