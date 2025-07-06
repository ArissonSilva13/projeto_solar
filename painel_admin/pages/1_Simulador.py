import streamlit as st

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Simulador Solar", layout="centered")

st.title(" Simulador de Produção de Energia Solar")

st.sidebar.header("⚙️ Configurações")
data_base = st.sidebar.date_input("Selecionar data", value=datetime.today())
intensidade_sol = st.sidebar.slider("Intensidade solar (%)", 50, 150, 100)
consumo_base = st.sidebar.slider("Consumo médio (kWh)", 1.0, 10.0, 4.0)

@st.cache_data
def gerar_dados(data, intensidade, consumo_medio):
    horas = pd.date_range(start=pd.Timestamp(data), periods=24, freq="h")
    gerado = np.random.uniform(1, 8, size=24) * (intensidade / 100)
    consumido = np.random.normal(loc=consumo_medio, scale=1.2, size=24)
    df = pd.DataFrame({
        "Hora": horas,
        "Gerado (kWh)": np.round(gerado, 2),
        "Consumido (kWh)": np.round(consumido, 2),
    })
    df["Excedente (kWh)"] = np.round(df["Gerado (kWh)"] - df["Consumido (kWh)"], 2)
    return df

dados = gerar_dados(data_base, intensidade_sol, consumo_base)

st.info("🚨 Para visualizar alertas detalhados, acesse a página **Alertas** no menu lateral.")

col1, col2, col3 = st.columns(3)
col1.metric("🔋 Total Gerado", f"{dados['Gerado (kWh)'].sum():.2f} kWh")
col2.metric("⚡ Total Consumido", f"{dados['Consumido (kWh)'].sum():.2f} kWh")
col3.metric("➕ Excedente Total", f"{dados['Excedente (kWh)'].sum():.2f} kWh")

st.subheader("📈 Produção vs Consumo por Hora")
st.line_chart(dados.set_index("Hora")[["Gerado (kWh)", "Consumido (kWh)", "Excedente (kWh)"]])

st.subheader("Dados Detalhados")
st.dataframe(dados.style.format({
    "Gerado (kWh)": "{:.2f}",
    "Consumido (kWh)": "{:.2f}",
    "Excedente (kWh)": "{:.2f}"
}))
