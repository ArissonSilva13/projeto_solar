import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Importa módulos internos
try:
    from painel_admin.alertas import SistemaAlertas
    from painel_admin.notificacoes import NotificacaoRealTime
except ImportError:
    # Fallback caso a estrutura de pastas varie levemente
    from alertas import SistemaAlertas
    from notificacoes import NotificacaoRealTime

from shared import aplicar_estilo_solar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central de Alertas", page_icon="🚨", layout="wide")
aplicar_estilo_solar() # Aplica o CSS Global

# Paleta de Cores (Consistente com Relatórios)
CORES = {
    "critico": "#EF4444",   # Vermelho
    "alerta": "#F59E0B",    # Laranja/Amarelo
    "normal": "#10B981",    # Verde
    "neutro": "#3B82F6"     # Azul
}

# --- VALIDAÇÃO DE LOGIN ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Acesso restrito. Por favor, faça login.")
    st.stop()

st.title("🚨 Central de Monitoramento e Alertas")
st.markdown("Monitoramento em tempo real de anomalias, saúde do sistema e histórico de incidentes.")

# --- INICIALIZAÇÃO DE CLASSES ---
sistema_alertas = SistemaAlertas()
# Tenta inicializar notificações, se falhar (arquivo faltando), cria mock
try:
    notificacao_system = NotificacaoRealTime()
except:
    class MockNotificacao:
        def verificar_alertas_excedente(self, *args): pass
        def exibir_painel_notificacoes(self): pass
        def auto_refresh_alertas(self): pass
        def limpar_notificacoes_antigas(self): pass
    notificacao_system = MockNotificacao()

# --- SIDEBAR: CONFIGURAÇÕES ---
with st.sidebar:
    st.header("⚙️ Parâmetros de Segurança")
    
    with st.expander("🎯 Limites de Disparo", expanded=True):
        deficit_critico = st.slider("Déficit Crítico (kWh)", -10.0, 0.0, -2.0, 0.5, help="Déficit diário considerado grave.")
        percentual_critico = st.slider("% Tempo em Déficit", 10, 80, 25, 5, help="% do dia operando no negativo.")
        horas_criticas = st.slider("Horas Consecutivas", 1, 12, 6, 1)
        
        # Atualiza a classe backend
        sistema_alertas.configurar_limites(
            deficit_critico=deficit_critico,
            percentual_critico=float(percentual_critico),
            horas_criticas=horas_criticas
        )

    st.subheader("📅 Período de Análise")
    col_d1, col_d2 = st.columns(2)
    data_inicio = col_d1.date_input("Início", value=datetime.today() - timedelta(days=7))
    data_fim = col_d2.date_input("Fim", value=datetime.today())

# --- GERADOR DE DADOS (CORRIGIDO) ---
@st.cache_data
def gerar_dados_historicos(data_inicio, data_fim, intensidade_base=100):
    dados_completos = []
    num_dias_calc = (data_fim - data_inicio).days + 1
    
    for dia in range(num_dias_calc):
        data_atual = data_inicio + timedelta(days=dia)
        # Variação aleatória do dia (chuva vs sol)
        intensidade_dia = intensidade_base * np.random.uniform(0.6, 1.4)
        
        horas = pd.date_range(start=pd.Timestamp(data_atual), periods=24, freq="h")
        hora_do_dia = np.arange(24)
        
        # Curva solar (Senoide)
        padrao_solar = np.maximum(0, np.sin(np.pi * (hora_do_dia - 6) / 12))
        gerado = padrao_solar * np.random.uniform(0.8, 1.2, 24) * (intensidade_dia / 100) * 5
        
        # Curva consumo (Picos manhã e noite)
        padrao_consumo = 2 + 2 * np.sin(np.pi * hora_do_dia / 12) + np.random.normal(0, 0.5, 24)
        # --- CORREÇÃO AQUI: Nome da variável corrigido para 'consumido' ---
        consumido = np.maximum(0.5, padrao_consumo) 
        
        df_dia = pd.DataFrame({
            "Data": [pd.to_datetime(data_atual)] * 24,
            "Hora": horas,
            "Gerado (kWh)": np.round(gerado, 2),
            "Consumido (kWh)": np.round(consumido, 2), # Agora 'consumido' existe!
        })
        df_dia["Excedente (kWh)"] = np.round(df_dia["Gerado (kWh)"] - df_dia["Consumido (kWh)"], 2)
        dados_completos.append(df_dia)
    
    return pd.concat(dados_completos, ignore_index=True) if dados_completos else pd.DataFrame()

# Gera dados
try:
    dados_historicos = gerar_dados_historicos(data_inicio, data_fim)
    dados_historicos['Data'] = pd.to_datetime(dados_historicos['Data'])
except Exception as e:
    st.error(f"Erro na simulação de dados: {e}")
    st.stop()

# --- SELEÇÃO DE DATA ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtro de Data")
datas_disponiveis = sorted(dados_historicos['Data'].dt.date.unique())
data_selecionada = st.sidebar.selectbox("Analisar Dia Específico", datas_disponiveis, index=len(datas_disponiveis)-1)

# Filtra dados do dia
dados_dia = dados_historicos[dados_historicos['Data'].dt.date == data_selecionada].copy()

# Processa alertas do dia selecionado
analise_dia = None
if not dados_dia.empty:
    analise_dia = sistema_alertas.analisar_excedente(dados_dia)
    notificacao_system.verificar_alertas_excedente(dados_dia)

# --- INTERFACE PRINCIPAL (ABAS) ---
tab1, tab2, tab3 = st.tabs(["🚨 Monitoramento Diário", "📊 Análise de Tendências", "📋 Histórico de Incidentes"])

# === ABA 1: MONITORAMENTO DIÁRIO ===
with tab1:
    st.markdown(f"### Status do Sistema: **{data_selecionada.strftime('%d/%m/%Y')}**")
    
    if not dados_dia.empty and analise_dia:
        # 1. KPIs em Cards Estilizados
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("☀️ Total Gerado", f"{dados_dia['Gerado (kWh)'].sum():.2f} kWh")
            c2.metric("🏠 Total Consumido", f"{dados_dia['Consumido (kWh)'].sum():.2f} kWh")
            
            saldo = dados_dia['Excedente (kWh)'].sum()
            c3.metric("🔋 Saldo do Dia", f"{saldo:.2f} kWh", 
                     delta="Déficit" if saldo < 0 else "Superávit", 
                     delta_color="normal" if saldo >= 0 else "inverse")
            
            horas_deficit = len(dados_dia[dados_dia['Excedente (kWh)'] < 0])
            c4.metric("⏰ Horas em Déficit", f"{horas_deficit}h", 
                     delta="Crítico" if horas_deficit > horas_criticas else "Normal",
                     delta_color="inverse")

        # 2. Área de Alertas e Gráfico
        col_alertas, col_grafico = st.columns([1, 1.5])
        
        with col_alertas:
            # Chama o método visual da classe (Cards de Alerta)
            sistema_alertas.exibir_alertas()
            
            # Recomendações logo abaixo dos alertas
            st.divider()
            sistema_alertas.gerar_recomendacoes(analise_dia)

        with col_grafico:
            st.subheader("📉 Balanço Energético Horário")
            
            # Gráfico visualmente rico
            colors = [CORES['critico'] if x < deficit_critico else CORES['alerta'] if x < 0 else CORES['normal'] for x in dados_dia['Excedente (kWh)']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dados_dia['Hora'].dt.strftime('%H:%M'),
                y=dados_dia['Excedente (kWh)'],
                marker_color=colors,
                name='Saldo Energético',
                hovertemplate='%{x}<br>Saldo: %{y:.2f} kWh'
            ))
            
            # Linhas de referência
            fig.add_hline(y=deficit_critico, line_dash="dash", line_color=CORES['critico'], annotation_text="Limite Crítico")
            fig.add_hline(y=0, line_color="#9CA3AF", line_width=1)
            
            fig.update_layout(
                xaxis_title="Horário",
                yaxis_title="Excedente (kWh)",
                height=500,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

        # 3. Tabela Detalhada com Barras Visuais
        st.subheader("📋 Detalhamento Horário")
        
        df_table = dados_dia[['Hora', 'Gerado (kWh)', 'Consumido (kWh)', 'Excedente (kWh)']].copy()
        df_table['Hora'] = df_table['Hora'].dt.strftime('%H:%M')
        
        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Hora": st.column_config.TextColumn("Horário"),
                "Gerado (kWh)": st.column_config.NumberColumn("Geração", format="%.2f kWh"),
                "Consumido (kWh)": st.column_config.NumberColumn("Consumo", format="%.2f kWh"),
                "Excedente (kWh)": st.column_config.ProgressColumn(
                    "Status do Saldo",
                    help="Barras vermelhas indicam déficit, verdes indicam sobra.",
                    format="%.2f kWh",
                    min_value=float(df_table['Excedente (kWh)'].min()),
                    max_value=float(df_table['Excedente (kWh)'].max()),
                )
            }
        )

# === ABA 2: TENDÊNCIAS ===
with tab2:
    st.header("📈 Análise de Tendências")
    
    # Processa dados para todos os dias
    analise_diaria = []
    for d in datas_disponiveis:
        d_temp = dados_historicos[dados_historicos['Data'].dt.date == d].copy()
        if not d_temp.empty:
            a_temp = sistema_alertas.analisar_excedente(d_temp)
            a_temp['data'] = d
            analise_diaria.append(a_temp)
    
    if analise_diaria:
        df_trend = pd.DataFrame(analise_diaria)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Evolução do Saldo Diário")
            fig_trend = px.line(df_trend, x='data', y='excedente_total', markers=True)
            fig_trend.update_traces(line_color=CORES['neutro'], line_width=3)
            fig_trend.add_hline(y=0, line_color=CORES['critico'], line_dash="dot")
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with col2:
            st.markdown("##### Horas Críticas por Dia")
            fig_bar = px.bar(df_trend, x='data', y='horas_deficit', 
                            color='horas_deficit', color_continuous_scale='OrRd')
            st.plotly_chart(fig_bar, use_container_width=True)

# === ABA 3: HISTÓRICO ===
with tab3:
    st.header("🗄️ Log de Incidentes")
    
    # Gera histórico de alertas completo
    todos_alertas = []
    for d in datas_disponiveis:
        d_temp = dados_historicos[dados_historicos['Data'].dt.date == d].copy()
        if not d_temp.empty:
            sis_temp = SistemaAlertas()
            sis_temp.configurar_limites(deficit_critico=deficit_critico)
            sis_temp.analisar_excedente(d_temp)
            for al in sis_temp.alertas:
                al['data_ref'] = d
                todos_alertas.append(al)
    
    if todos_alertas:
        df_log = pd.DataFrame(todos_alertas)
        
        # Filtros
        c1, c2 = st.columns(2)
        filtro_tipo = c1.multiselect("Filtrar Tipo", df_log['tipo'].unique(), default=df_log['tipo'].unique())
        
        df_show = df_log[df_log['tipo'].isin(filtro_tipo)]
        
        st.dataframe(
            df_show[['data_ref', 'horario', 'tipo', 'mensagem', 'valor']],
            use_container_width=True,
            column_config={
                "tipo": st.column_config.Column(
                    "Severidade",
                    width="small",
                    help="Nível do alerta"
                ),
                "data_ref": st.column_config.DateColumn("Data"),
            }
        )
        
        # Botão Download
        st.download_button(
            "📥 Baixar Log Completo (CSV)",
            df_log.to_csv(index=False),
            "historico_alertas.csv",
            "text/csv"
        )
    else:
        st.success("Nenhum incidente registrado no período.")

# --- SIDEBAR: RODAPÉ ---
st.sidebar.divider()
notificacao_system.exibir_painel_notificacoes()