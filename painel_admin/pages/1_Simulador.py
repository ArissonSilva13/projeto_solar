import streamlit as st

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import locale

# Configurar localização brasileira para formatação de moeda
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

def format_currency(value):
    """Formatar valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(page_title="Simulador Solar", layout="centered")

st.markdown("""
<style>
[data-testid="metric-container"] {
    font-size: 0.6rem !important;
}
[data-testid="metric-container"] > div {
    font-size: 0.6rem !important;
}
[data-testid="metric-container"] label {
    font-size: 0.75rem !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 0.8rem !important;
}
        
.st-emotion-cache-efbu8t{
    font-size: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("☀️ Simulador de Produção de Energia Solar")

st.sidebar.header("⚙️ Configurações")
data_base = st.sidebar.date_input("Selecionar data", value=datetime.today())
intensidade_sol = st.sidebar.slider("Intensidade solar (%)", 50, 150, 100)
consumo_base = st.sidebar.slider("Consumo médio (kWh)", 1.0, 10.0, 4.0)

st.sidebar.header("💰 Configurações Financeiras")
tarifa_normal = st.sidebar.number_input("Tarifa normal (R$/kWh)", value=0.65, step=0.01, format="%.2f")
tarifa_pico = st.sidebar.number_input("Tarifa pico (R$/kWh)", value=0.85, step=0.01, format="%.2f")
tarifa_compensacao = st.sidebar.number_input("Tarifa compensação (R$/kWh)", value=0.50, step=0.01, format="%.2f")
investimento_inicial = st.sidebar.number_input("Investimento inicial (R$)", value=15000.0, step=500.0, format="%.2f")

@st.cache_data
def gerar_dados(data, intensidade, consumo_medio):
    horas = pd.date_range(start=pd.Timestamp(data), periods=24, freq="h")
    gerado = np.random.uniform(1, 8, size=24) * (intensidade / 100)
    consumido = np.random.normal(loc=consumo_medio, scale=1.2, size=24)
    
    # Definir horários de pico (18h às 21h)
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
    # Calcular economia por não consumir energia da rede
    df["Economia_Consumo"] = df.apply(
        lambda row: min(row["Gerado (kWh)"], row["Consumido (kWh)"]) * 
        (tarifa_pico if row["Horario_Pico"] else tarifa_normal), 
        axis=1
    )
    
    # Calcular ganho pela energia excedente injetada na rede
    df["Ganho_Excedente"] = df.apply(
        lambda row: max(0, row["Excedente (kWh)"]) * tarifa_compensacao,
        axis=1
    )
    
    # Calcular custo se tivesse que comprar energia da rede
    df["Custo_Sem_Solar"] = df.apply(
        lambda row: row["Consumido (kWh)"] * 
        (tarifa_pico if row["Horario_Pico"] else tarifa_normal),
        axis=1
    )
    
    # Calcular custo real (só o que não foi gerado)
    df["Custo_Real"] = df.apply(
        lambda row: max(0, row["Consumido (kWh)"] - row["Gerado (kWh)"]) * 
        (tarifa_pico if row["Horario_Pico"] else tarifa_normal),
        axis=1
    )
    
    # Economia total por hora
    df["Economia_Total"] = df["Economia_Consumo"] + df["Ganho_Excedente"]
    
    return df

dados = gerar_dados(data_base, intensidade_sol, consumo_base)
dados_financeiro = calcular_financeiro(dados, tarifa_normal, tarifa_pico, tarifa_compensacao)

st.info("🚨 Para visualizar alertas detalhados, acesse a página **Alertas** no menu lateral.")

# Gráficos primeiro
st.subheader("📈 Produção vs Consumo por Hora")
st.line_chart(dados_financeiro.set_index("Hora")[["Gerado (kWh)", "Consumido (kWh)", "Excedente (kWh)"]])

st.subheader("💵 Ganhos Financeiros por Hora")
st.line_chart(dados_financeiro.set_index("Hora")[["Economia_Consumo", "Ganho_Excedente", "Economia_Total"]])

# Métricas principais
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔋 Total Gerado", f"{dados_financeiro['Gerado (kWh)'].sum():.2f} kWh")
col2.metric("⚡ Total Consumido", f"{dados_financeiro['Consumido (kWh)'].sum():.2f} kWh")
col3.metric("➕ Excedente Total", f"{dados_financeiro['Excedente (kWh)'].sum():.2f} kWh")
col4.metric("💰 Economia Diária", format_currency(dados_financeiro['Economia_Total'].sum()))

# Cálculos de projeções
economia_diaria = dados_financeiro['Economia_Total'].sum()
economia_mensal = economia_diaria * 30
economia_anual = economia_diaria * 365
tempo_retorno = investimento_inicial / economia_anual if economia_anual > 0 else float('inf')

st.subheader("📊 Projeções Financeiras")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📈 Economia Mensal", format_currency(economia_mensal))
col2.metric("📈 Economia Anual", format_currency(economia_anual))
col3.metric("⏰ Tempo de Retorno", f"{tempo_retorno:.1f} anos" if tempo_retorno != float('inf') else "N/A")
col4.metric("💵 Economia em 25 anos", format_currency(economia_anual * 25))

# Breakdown financeiro
st.subheader("💰 Breakdown Financeiro Diário")
col1, col2, col3 = st.columns(3)
col1.metric("💡 Economia no Consumo", format_currency(dados_financeiro['Economia_Consumo'].sum()))
col2.metric("🔄 Ganho Excedente", format_currency(dados_financeiro['Ganho_Excedente'].sum()))
col3.metric("🔻 Redução na Conta", format_currency(dados_financeiro['Custo_Sem_Solar'].sum() - dados_financeiro['Custo_Real'].sum()))

st.subheader("📋 Dados Detalhados")
dados_exibicao = dados_financeiro.copy()
dados_exibicao["Hora"] = dados_exibicao["Hora"].dt.strftime("%H:%M")
dados_exibicao["Horário"] = dados_exibicao["Horario_Pico"].map({True: "Pico", False: "Normal"})

# Formatar valores monetários na tabela
for col in ["Economia_Consumo", "Ganho_Excedente", "Economia_Total"]:
    dados_exibicao[col] = dados_exibicao[col].apply(format_currency)

st.dataframe(dados_exibicao[[
    "Hora", "Horário", "Gerado (kWh)", "Consumido (kWh)", "Excedente (kWh)",
    "Economia_Consumo", "Ganho_Excedente", "Economia_Total"
]].style.format({
    "Gerado (kWh)": "{:.2f}",
    "Consumido (kWh)": "{:.2f}",
    "Excedente (kWh)": "{:.2f}"
}))

# Análise de viabilidade
st.subheader("📊 Análise de Viabilidade")
if tempo_retorno != float('inf'):
    if tempo_retorno <= 5:
        st.success(f"🎯 **Excelente investimento!** Payback em {tempo_retorno:.1f} anos.")
    elif tempo_retorno <= 8:
        st.info(f"👍 **Bom investimento!** Payback em {tempo_retorno:.1f} anos.")
    elif tempo_retorno <= 12:
        st.warning(f"⚠️ **Investimento moderado.** Payback em {tempo_retorno:.1f} anos.")
    else:
        st.error(f"❌ **Investimento de alto risco.** Payback em {tempo_retorno:.1f} anos.")
else:
    st.error("❌ **Inviável:** O sistema não gera economia suficiente.")

# Resumo executivo
with st.expander("📋 Resumo Executivo"):
    st.write(f"""
    **Resumo da Simulação:**
    
    - **Investimento inicial:** {format_currency(investimento_inicial)}
    - **Economia diária:** {format_currency(economia_diaria)}
    - **Economia mensal:** {format_currency(economia_mensal)}
    - **Economia anual:** {format_currency(economia_anual)}
    - **Tempo de retorno:** {tempo_retorno:.1f} anos
    - **Economia em 25 anos:** {format_currency(economia_anual * 25)}
    - **ROI em 25 anos:** {((economia_anual * 25 - investimento_inicial) / investimento_inicial * 100):.1f}%
    
    **Configurações utilizadas:**
    - Tarifa normal: {format_currency(tarifa_normal)}/kWh
    - Tarifa pico: {format_currency(tarifa_pico)}/kWh
    - Tarifa compensação: {format_currency(tarifa_compensacao)}/kWh
    - Intensidade solar: {intensidade_sol}%
    - Consumo médio: {consumo_base} kWh
    """)
