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
    try:
        from alertas import SistemaAlertas
        from notificacoes import NotificacaoRealTime
    except:
        # Mock para evitar erros visuais se o backend falhar
        class MockNotificacao:
            def verificar_alertas_excedente(self, *args): pass
            def exibir_painel_notificacoes(self): pass
            def auto_refresh_alertas(self): pass
            def limpar_notificacoes_antigas(self): pass
        notificacao_system = MockNotificacao()
        class SistemaAlertas: # Mock básico
            def __init__(self): self.alertas = []
            def configurar_limites(self, **kwargs): pass
            def analisar_excedente(self, df): return {}
            def exibir_alertas(self): pass
            def gerar_recomendacoes(self, a): pass

from shared import aplicar_estilo_solar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Central de Monitoramento", page_icon="⚡", layout="wide")
aplicar_estilo_solar()

# --- CSS PERSONALIZADO PARA ALERTAS ---
# Isso corrige o problema das "bolinhas" ficando em cima do texto
st.markdown("""
<style>
    .alert-card {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid #ccc;
        background-color: #f8f9fa;
        display: flex;
        align-items: start;
        gap: 15px;
    }
    .alert-critico { border-left-color: #EF4444; background-color: #FEF2F2; }
    .alert-moderado { border-left-color: #F59E0B; background-color: #FFFBEB; }
    .alert-atencao { border-left-color: #3B82F6; background-color: #EFF6FF; }
    
    .alert-title { font-weight: 600; font-size: 14px; margin-bottom: 2px; color: #1f2937; }
    .alert-time { font-size: 12px; color: #6b7280; font-family: monospace; }
    .alert-value { font-size: 13px; color: #374151; }
</style>
""", unsafe_allow_html=True)

# Paleta de Cores
CORES = {
    "critico": "#EF4444",   # Vermelho
    "alerta": "#F59E0B",    # Laranja
    "normal": "#10B981",    # Verde
    "neutro": "#3B82F6"     # Azul
}

# --- VALIDAÇÃO DE LOGIN ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Acesso restrito. Faça login.")
    st.stop()

# --- HELPER PARA ÍCONES SVG GERAIS ---
def render_icon(svg_path, title, color="#1E3A8A"):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            {svg_path}
        </svg>
        <h4 style="margin: 0; color: #1E3A8A; font-weight: 600; font-family: sans-serif;">{title}</h4>
    </div>
    """, unsafe_allow_html=True)

# --- HELPER PARA RENDERIZAR CARD DE ALERTA (SUBSTITUI EMOJIS) ---
def render_alert_card(tipo, mensagem, horario, valor=None):
    if tipo == 'critico':
        css_class = "alert-critico"
        # SVG: Alert Circle
        icon_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>'
    elif tipo == 'moderado':
        css_class = "alert-moderado"
        # SVG: Alert Triangle
        icon_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
    else:
        css_class = "alert-atencao"
        # SVG: Info
        icon_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'

    val_str = f" • Valor: {valor:.2f}" if valor is not None else ""
    
    st.markdown(f"""
    <div class="alert-card {css_class}">
        <div style="min-width: 20px; margin-top: 2px;">{icon_svg}</div>
        <div>
            <div class="alert-title">{mensagem}</div>
            <div class="alert-time">{horario} {val_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.title("Monitoramento de Anomalias")
st.markdown("Gestão de incidentes e saúde do sistema em tempo real.")

# --- INICIALIZAÇÃO DE CLASSES ---
sistema_alertas = SistemaAlertas()
try:
    notificacao_system = NotificacaoRealTime()
except:
    pass

# --- SIDEBAR: CONFIGURAÇÕES ---
with st.sidebar:
    st.header("Configurações de Segurança")
    
    # SVG: Settings/Sliders
    render_icon('<line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line>', "Limites de Disparo", "#FF8C00")
    
    with st.expander("Parâmetros Avançados", expanded=True):
        deficit_critico = st.slider("Déficit Crítico (kWh)", -10.0, 0.0, -2.0, 0.5)
        percentual_critico = st.slider("% Tempo em Déficit", 10, 80, 25, 5)
        horas_criticas = st.slider("Horas Consecutivas", 1, 12, 6, 1)
        
        sistema_alertas.configurar_limites(
            deficit_critico=deficit_critico,
            percentual_critico=float(percentual_critico),
            horas_criticas=horas_criticas
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # SVG: Calendar
    render_icon('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>', "Período de Análise", "#1E3A8A")
    
    col_d1, col_d2 = st.columns(2)
    data_inicio = col_d1.date_input("Início", value=datetime.today() - timedelta(days=7))
    data_fim = col_d2.date_input("Fim", value=datetime.today())

# --- GERADOR DE DADOS ---
@st.cache_data
def gerar_dados_historicos(data_inicio, data_fim, intensidade_base=100):
    dados_completos = []
    num_dias_calc = (data_fim - data_inicio).days + 1
    
    for dia in range(num_dias_calc):
        data_atual = data_inicio + timedelta(days=dia)
        intensidade_dia = intensidade_base * np.random.uniform(0.6, 1.4)
        
        horas = pd.date_range(start=pd.Timestamp(data_atual), periods=24, freq="h")
        hora_do_dia = np.arange(24)
        
        padrao_solar = np.maximum(0, np.sin(np.pi * (hora_do_dia - 6) / 12))
        gerado = padrao_solar * np.random.uniform(0.8, 1.2, 24) * (intensidade_dia / 100) * 5
        
        padrao_consumo = 2 + 2 * np.sin(np.pi * hora_do_dia / 12) + np.random.normal(0, 0.5, 24)
        consumido = np.maximum(0.5, padrao_consumo) 
        
        df_dia = pd.DataFrame({
            "Data": [pd.to_datetime(data_atual)] * 24,
            "Hora": horas,
            "Gerado (kWh)": np.round(gerado, 2),
            "Consumido (kWh)": np.round(consumido, 2),
        })
        df_dia["Excedente (kWh)"] = np.round(df_dia["Gerado (kWh)"] - df_dia["Consumido (kWh)"], 2)
        dados_completos.append(df_dia)
    
    return pd.concat(dados_completos, ignore_index=True) if dados_completos else pd.DataFrame()

try:
    dados_historicos = gerar_dados_historicos(data_inicio, data_fim)
    dados_historicos['Data'] = pd.to_datetime(dados_historicos['Data'])
except Exception as e:
    st.error(f"Erro na simulação: {e}")
    st.stop()

# --- FILTRO DE DATA ---
st.sidebar.markdown("---")
render_icon('<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>', "Zoom em Data Específica")
datas_disponiveis = sorted(dados_historicos['Data'].dt.date.unique())
data_selecionada = st.sidebar.selectbox("Selecionar Dia", datas_disponiveis, index=len(datas_disponiveis)-1, label_visibility="collapsed")

dados_dia = dados_historicos[dados_historicos['Data'].dt.date == data_selecionada].copy()

analise_dia = None
if not dados_dia.empty:
    analise_dia = sistema_alertas.analisar_excedente(dados_dia)
    try:
        notificacao_system.verificar_alertas_excedente(dados_dia)
    except: pass

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["Monitoramento Diário", "Análise de Tendências", "Log de Incidentes"])

# === ABA 1: MONITORAMENTO ===
with tab1:
    st.markdown(f"**Data de Referência:** {data_selecionada.strftime('%d/%m/%Y')}")
    
    if not dados_dia.empty and analise_dia:
        # SVG: Activity
        render_icon('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>', "Indicadores de Saúde")
        
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Gerado", f"{dados_dia['Gerado (kWh)'].sum():.2f} kWh")
            c2.metric("Total Consumido", f"{dados_dia['Consumido (kWh)'].sum():.2f} kWh")
            
            saldo = dados_dia['Excedente (kWh)'].sum()
            c3.metric("Saldo do Dia", f"{saldo:.2f} kWh", 
                     delta="Déficit" if saldo < 0 else "Superávit", 
                     delta_color="normal" if saldo >= 0 else "inverse")
            
            horas_deficit = len(dados_dia[dados_dia['Excedente (kWh)'] < 0])
            c4.metric("Horas em Déficit", f"{horas_deficit}h", 
                     delta="Crítico" if horas_deficit > horas_criticas else "Normal",
                     delta_color="inverse")

        col_alertas, col_grafico = st.columns([1, 1.5])
        
        with col_alertas:
            st.markdown("<br>", unsafe_allow_html=True)
            # Título da seção de alertas
            render_icon('<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>', "Alertas Ativos", "#EF4444")
            
            # --- RENDERIZAÇÃO MANUAL DOS ALERTAS (Substitui sistema_alertas.exibir_alertas) ---
            if sistema_alertas.alertas:
                # Ordena: críticos primeiro
                alertas_sorted = sorted(sistema_alertas.alertas, key=lambda x: 0 if x['tipo'] == 'critico' else 1)
                
                # Container com altura fixa e scroll para muitos alertas
                with st.container(height=400):
                    for alerta in alertas_sorted:
                        render_alert_card(
                            alerta['tipo'], 
                            alerta['mensagem'], 
                            alerta['horario'], 
                            alerta.get('valor')
                        )
            else:
                st.success("Nenhuma anomalia detectada.")
            
            st.divider()
            
            # --- RECOMENDAÇÕES CLEAN ---
            st.markdown("#####  Recomendações do Sistema")
            alertas_criticos = [a for a in sistema_alertas.alertas if a['tipo'] == 'critico']
            
            if alertas_criticos:
                st.warning("Ação Imediata: Verifique inversores e reduza cargas não essenciais.")
            elif analise_dia.get('horas_sem_excedente', 0) > 0:
                st.info("Sugestão: Otimize o consumo para horários de pico solar.")
            else:
                st.success("Operação otimizada. Mantenha o monitoramento.")

        with col_grafico:
            st.markdown("<br>", unsafe_allow_html=True)
            render_icon('<rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>', "Balanço Energético Horário")
            
            colors = [CORES['critico'] if x < deficit_critico else CORES['alerta'] if x < 0 else CORES['normal'] for x in dados_dia['Excedente (kWh)']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dados_dia['Hora'].dt.strftime('%H:%M'),
                y=dados_dia['Excedente (kWh)'],
                marker_color=colors,
                name='Saldo',
                hovertemplate='%{x}<br>Saldo: %{y:.2f} kWh'
            ))
            
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

        st.markdown("<br>", unsafe_allow_html=True)
        render_icon('<line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line>', "Detalhamento Horário")
        
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
                    format="%.2f kWh",
                    min_value=float(df_table['Excedente (kWh)'].min()),
                    max_value=float(df_table['Excedente (kWh)'].max()),
                )
            }
        )

# === ABA 2: TENDÊNCIAS ===
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    render_icon('<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline>', "Tendência Histórica")
    
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
    st.markdown("<br>", unsafe_allow_html=True)
    render_icon('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>', "Log de Incidentes")
    
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
        
        c1, c2 = st.columns(2)
        filtro_tipo = c1.multiselect("Filtrar Severidade", df_log['tipo'].unique(), default=df_log['tipo'].unique())
        
        df_show = df_log[df_log['tipo'].isin(filtro_tipo)]
        
        st.dataframe(
            df_show[['data_ref', 'horario', 'tipo', 'mensagem', 'valor']],
            use_container_width=True,
            column_config={
                "tipo": st.column_config.Column("Nível", width="small"),
                "data_ref": st.column_config.DateColumn("Data"),
                "mensagem": st.column_config.TextColumn("Descrição do Evento", width="large")
            }
        )
        
        st.download_button(
            "Baixar Log (CSV)",
            df_log.to_csv(index=False),
            "historico_alertas.csv",
            "text/csv"
        )
    else:
        st.info("Nenhum incidente registrado no período.")

# --- RODAPÉ DA SIDEBAR ---
st.sidebar.divider()
try:
    # Tenta usar notificações se disponível, mas de forma discreta
    # notificacao_system.exibir_painel_notificacoes() # Comentado para evitar poluição visual com emojis antigos
    pass
except: pass