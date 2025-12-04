import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import locale
from shared import aplicar_estilo_solar

# --- CONFIGURAÇÃO INICIAL ---
# Troquei o solzinho por um ícone de raio (mais técnico) ou poderia ser o logo da empresa
st.set_page_config(page_title="Simulador Solar", page_icon="⚡", layout="wide")

# Aplica o CSS Global
aplicar_estilo_solar()

# --- VERIFICAÇÃO DE LOGIN ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error(" Acesso restrito. Faça login.")
    st.stop()

# --- HELPER PARA ÍCONES SVG (NOVO) ---
# Esta função desenha ícones nítidos em vez de usar emojis
def render_icon(svg_path, title, color="#1E3A8A"):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            {svg_path}
        </svg>
        <h4 style="margin: 0; color: #1E3A8A; font-weight: 600; font-family: sans-serif;">{title}</h4>
    </div>
    """, unsafe_allow_html=True)

# --- FUNÇÕES UTILITÁRIAS ---
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- SIDEBAR (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("Parâmetros de Simulação") # Texto limpo
    data_base = st.date_input("Data de Referência", value=datetime.today())
    
    st.markdown("---")
    
    # Ícone SVG: Sol (Laranja)
    render_icon(
        '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>', 
        "Captação Solar", 
        color="#FF8C00"
    )
    intensidade_sol = st.slider("Eficiência (%)", 50, 150, 100, help="100% considera irradiação plena.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ícone SVG: Casa/Consumo (Azul)
    render_icon(
        '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline>', 
        "Perfil de Consumo"
    )
    consumo_base = st.slider("Média Horária (kWh)", 1.0, 10.0, 4.0)

    st.markdown("<br>", unsafe_allow_html=True)

    # Ícone SVG: Moeda/Tarifas (Verde)
    render_icon(
        '<line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>', 
        "Dados Financeiros",
        color="#10B981"
    )
    tarifa_normal = st.number_input("Tarifa Normal (R$/kWh)", value=0.65, step=0.01, format="%.2f")
    tarifa_pico = st.number_input("Tarifa Pico (R$/kWh)", value=0.85, step=0.01, format="%.2f")
    tarifa_compensacao = st.number_input("Tarifa Compensação (R$/kWh)", value=0.50, step=0.01, format="%.2f")
    investimento_inicial = st.number_input("Investimento Inicial (R$)", value=15000.0, step=500.0, format="%.2f")

# --- LÓGICA DE DADOS (MANTIDA 100% IGUAL) ---
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
# Título limpo, sem emoji
st.title("Simulador de Produção")
st.markdown("Acompanhe a projeção de geração de energia e economia financeira baseada nos parâmetros laterais.")

# --- GRÁFICOS LADO A LADO ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    # SVG: Gráfico de Linha
    render_icon('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>', "Produção vs Consumo (24h)", "#FF8C00")
    
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
    # SVG: Gráfico de Barras
    render_icon('<line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line>', "Economia Acumulada", "#10B981")
    
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

# --- KPI CARDS (LIMPOS) ---
# SVG: Dashboard
render_icon('<rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect>', "Resultados Consolidados")

c1, c2, c3, c4 = st.columns(4)
# Métricas sem emojis no label
c1.metric("Total Gerado", f"{dados_financeiro['Gerado (kWh)'].sum():.2f} kWh")
c2.metric("Total Consumido", f"{dados_financeiro['Consumido (kWh)'].sum():.2f} kWh")
c3.metric("Saldo Excedente", f"{dados_financeiro['Excedente (kWh)'].sum():.2f} kWh")
c4.metric("Economia Hoje", format_currency(dados_financeiro['Economia_Total'].sum()))

# --- PROJEÇÕES FINANCEIRAS ---
economia_diaria = dados_financeiro['Economia_Total'].sum()
economia_mensal = economia_diaria * 30
economia_anual = economia_diaria * 365
tempo_retorno = investimento_inicial / economia_anual if economia_anual > 0 else float('inf')

st.markdown("<br>", unsafe_allow_html=True)

# SVG: Calendário/Alvo
render_icon('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>', "Projeção de Retorno (ROI)")

with st.container(border=True): # Caixa bonita
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Economia Mensal", format_currency(economia_mensal))
    col2.metric("Economia Anual", format_currency(economia_anual))
    col3.metric("Payback Estimado", f"{tempo_retorno:.1f} anos", 
                delta="Bom" if tempo_retorno < 5 else "Médio", delta_color="inverse")
    col4.metric("Economia em 25 Anos", format_currency(economia_anual * 25))

    # Barra de Progresso
    if tempo_retorno < 20:
        progresso = min(1.0, max(0.0, 1 - (tempo_retorno / 10))) 
        st.progress(progresso, text=f"Viabilidade do Investimento: {progresso*100:.0f}%")

# --- TABELA DE DADOS ---
st.markdown("<br>", unsafe_allow_html=True)
# SVG: Lista
render_icon('<line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line>', "Detalhamento Horário")

df_table = dados_financeiro[["Hora", "Gerado (kWh)", "Consumido (kWh)", "Economia_Total"]].copy()
df_table["Hora"] = df_table["Hora"].dt.strftime("%H:%M")

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

# --- RESUMO (Sem emoji no expander) ---
with st.expander("Relatório Executivo Completo"):
    st.markdown(f"""
    **Resumo da Simulação:**
    O sistema simulado com **{intensidade_sol}% de eficiência** gerou uma economia diária de **{format_currency(economia_diaria)}**.
    
    * **Investimento:** {format_currency(investimento_inicial)}
    * **Retorno em:** {tempo_retorno:.1f} anos
    * **Lucro Projetado (25 anos):** {format_currency((economia_anual * 25) - investimento_inicial)}
    * **ROI em 25 anos:** {((economia_anual * 25 - investimento_inicial) / investimento_inicial * 100):.1f}%
    
    **Configurações utilizadas:**
    - Tarifa normal: {format_currency(tarifa_normal)}/kWh
    - Tarifa pico: {format_currency(tarifa_pico)}/kWh
    - Tarifa compensação: {format_currency(tarifa_compensacao)}/kWh
    """)