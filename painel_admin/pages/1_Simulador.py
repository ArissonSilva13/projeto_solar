import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px  # <--- Nova biblioteca para gráficos bonitos
from datetime import datetime
import locale
from shared import aplicar_estilo_solar # <--- Importando nosso estilo

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Simulador Solar", page_icon="☀️", layout="wide") # Mudei para wide

# Aplica o CSS Global (Cards, Cores, etc)
aplicar_estilo_solar()

# --- VERIFICAÇÃO DE LOGIN ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("🔒 Você precisa estar logado para acessar esta página.")
    st.stop()

# --- FUNÇÕES UTILITÁRIAS ---
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- SIDEBAR (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Parâmetros de Simulação")
    data_base = st.date_input("Data da Simulação", value=datetime.today())
    
    st.markdown("### ☀️ Sistema Solar")
    intensidade_sol = st.slider("Intensidade Solar (%)", 50, 150, 100, help="100% é um dia de sol pleno.")
    
    st.markdown("### 🏠 Consumo")
    consumo_base = st.slider("Consumo Médio (kWh)", 1.0, 10.0, 4.0)

    st.markdown("### 💰 Tarifas (R$)")
    tarifa_normal = st.number_input("Tarifa Normal", value=0.65, step=0.01, format="%.2f")
    tarifa_pico = st.number_input("Tarifa Pico", value=0.85, step=0.01, format="%.2f")
    tarifa_compensacao = st.number_input("Tarifa Compensação", value=0.50, step=0.01, format="%.2f")
    investimento_inicial = st.number_input("Investimento Inicial", value=15000.0, step=500.0, format="%.2f")

# --- LÓGICA (MANTIDA IGUAL) ---
@st.cache_data
def gerar_dados(data, intensidade, consumo_medio):
    horas = pd.date_range(start=pd.Timestamp(data), periods=24, freq="h")
    # Pequeno ajuste para garantir que não gere negativo na aleatoriedade
    gerado = np.maximum(0, np.random.uniform(0, 8, size=24) * (intensidade / 100))
    # Zera geração à noite (aprox 19h as 06h) para realismo
    horas_noite = [h.hour < 6 or h.hour > 18 for h in horas]
    gerado[horas_noite] = 0
    
    consumido = np.maximum(0, np.random.normal(loc=consumo_medio, scale=1.2, size=24))
    
    horarios_pico = [(h.hour >= 18 and h.hour <= 21) for h in horas]
    
    df = pd.DataFrame({
        "Hora": horas,
        "Gerado (kWh)": np.round(gerado, 2),
        "Consumido (kWh)": np.round(consumido, 2),
        "Horario_Pico": horarios_pico
    })
    
    df["Excedente (kWh)"] = np.round(df["Gerado (kWh)"] - df["Consumido (kWh)"], 2)
    return df

@st.cache_data
def calcular_financeiro(df, tarifa_normal, tarifa_pico, tarifa_compensacao):
    df["Economia_Consumo"] = df.apply(
        lambda row: min(row["Gerado (kWh)"], row["Consumido (kWh)"]) * (tarifa_pico if row["Horario_Pico"] else tarifa_normal), 
        axis=1
    )
    
    df["Ganho_Excedente"] = df.apply(
        lambda row: max(0, row["Excedente (kWh)"]) * tarifa_compensacao,
        axis=1
    )
    
    df["Custo_Sem_Solar"] = df.apply(
        lambda row: row["Consumido (kWh)"] * (tarifa_pico if row["Horario_Pico"] else tarifa_normal),
        axis=1
    )
    
    df["Custo_Real"] = df.apply(
        lambda row: max(0, row["Consumido (kWh)"] - row["Gerado (kWh)"]) * (tarifa_pico if row["Horario_Pico"] else tarifa_normal),
        axis=1
    )
    
    df["Economia_Total"] = df["Economia_Consumo"] + df["Ganho_Excedente"]
    return df

# Processamento
dados = gerar_dados(data_base, intensidade_sol, consumo_base)
dados_financeiro = calcular_financeiro(dados, tarifa_normal, tarifa_pico, tarifa_compensacao)

# --- INTERFACE PRINCIPAL ---
st.title("☀️ Simulador de Produção Solar")
st.markdown("Acompanhe a projeção de geração de energia e economia financeira baseada nos parâmetros laterais.")

# --- GRÁFICOS LADO A LADO ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("##### 📈 Produção vs Consumo (24h)")
    # Gráfico Plotly Personalizado (Muito mais bonito que st.line_chart)
    fig_prod = px.area(
        dados_financeiro, 
        x="Hora", 
        y=["Gerado (kWh)", "Consumido (kWh)"],
        color_discrete_sequence=["#FF8C00", "#1E3A8A"], # Laranja e Azul
        labels={"value": "Energia (kWh)", "variable": "Legenda"}
    )
    fig_prod.update_layout(legend=dict(orientation="h", y=1.1, x=0), margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_prod, use_container_width=True)

with col_graf2:
    st.markdown("##### 💵 Economia Acumulada")
    fig_fin = px.bar(
        dados_financeiro, 
        x="Hora", 
        y="Economia_Total",
        color_discrete_sequence=["#10B981"], # Verde Dinheiro
        labels={"Economia_Total": "Economia (R$)"}
    )
    fig_fin.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_fin, use_container_width=True)

st.markdown("---")

# --- KPI CARDS (Vão pegar o estilo do shared.py) ---
st.subheader("📊 Resultados do Dia")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🔋 Total Gerado", f"{dados_financeiro['Gerado (kWh)'].sum():.2f} kWh")
c2.metric("⚡ Total Consumido", f"{dados_financeiro['Consumido (kWh)'].sum():.2f} kWh")
c3.metric("➕ Excedente", f"{dados_financeiro['Excedente (kWh)'].sum():.2f} kWh")
c4.metric("💰 Economia Hoje", format_currency(dados_financeiro['Economia_Total'].sum()))

# --- PROJEÇÕES FINANCEIRAS ---
economia_diaria = dados_financeiro['Economia_Total'].sum()
economia_mensal = economia_diaria * 30
economia_anual = economia_diaria * 365
tempo_retorno = investimento_inicial / economia_anual if economia_anual > 0 else float('inf')

st.markdown("### 📅 Projeção de Retorno (ROI)")
with st.container(border=True): # Cria uma caixa bonita em volta
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🗓️ Economia Mensal", format_currency(economia_mensal))
    col2.metric("📅 Economia Anual", format_currency(economia_anual))
    col3.metric("⏳ Payback Estimado", f"{tempo_retorno:.1f} anos", 
                delta="Bom" if tempo_retorno < 5 else "Médio", delta_color="inverse")
    col4.metric("💎 Economia 25 Anos", format_currency(economia_anual * 25))

    # Barra de Progresso do Payback
    if tempo_retorno < 20:
        progresso = min(1.0, max(0.0, 1 - (tempo_retorno / 10))) # Exemplo visual
        st.progress(progresso, text=f"Viabilidade do Investimento: {progresso*100:.0f}%")

# --- TABELA DE DADOS (DATA EDITOR COM FORMATAÇÃO) ---
st.subheader("📋 Detalhamento Horário")

# Prepara dados para a tabela
df_table = dados_financeiro[["Hora", "Gerado (kWh)", "Consumido (kWh)", "Economia_Total"]].copy()
df_table["Hora"] = df_table["Hora"].dt.strftime("%H:%M")

# Tabela Interativa Bonita
st.dataframe(
    df_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Hora": st.column_config.TextColumn("Horário"),
        "Gerado (kWh)": st.column_config.ProgressColumn(
            "Geração Solar",
            format="%.2f kWh",
            min_value=0,
            max_value=float(df_table["Gerado (kWh)"].max()),
        ),
        "Consumido (kWh)": st.column_config.NumberColumn(
            "Consumo",
            format="%.2f kWh",
        ),
        "Economia_Total": st.column_config.NumberColumn(
            "Economia (R$)",
            format="R$ %.2f",
        ),
    }
)

# --- RESUMO (EXPANDER) ---
with st.expander("📝 Ver Relatório Executivo Completo"):
    st.markdown(f"""
    **Resumo da Simulação:**
    O sistema simulado com **{intensidade_sol}% de eficiência solar** gerou uma economia diária de **{format_currency(economia_diaria)}**.
    
    * **Investimento:** {format_currency(investimento_inicial)}
    * **Retorno em:** {tempo_retorno:.1f} anos
    * **Lucro Projetado (25 anos):** {format_currency((economia_anual * 25) - investimento_inicial)}
    """)