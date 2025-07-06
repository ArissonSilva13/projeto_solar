import streamlit as st

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Você precisa estar logado para acessar esta página.")
    st.stop()

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from alertas import SistemaAlertas
from notificacoes import NotificacaoRealTime

st.set_page_config(page_title="Central de Alertas", layout="wide")

st.title("🚨 Central de Alertas e Monitoramento")

sistema_alertas = SistemaAlertas()
notificacao_system = NotificacaoRealTime()

st.sidebar.header("⚙️ Configurações de Alertas")

st.sidebar.subheader("🎯 Limites de Alertas")
deficit_critico = st.sidebar.slider("Déficit Crítico (kWh)", -10.0, 0.0, -2.0, 0.1)
deficit_moderado = st.sidebar.slider("Déficit Moderado (kWh)", -5.0, 0.0, 0.0, 0.1)
percentual_critico = st.sidebar.slider("Percentual Crítico (%)", 10.0, 50.0, 25.0, 1.0)
horas_criticas = st.sidebar.slider("Horas Críticas", 3, 12, 6, 1)

sistema_alertas.configurar_limites(
    deficit_critico=deficit_critico,
    deficit_moderado=deficit_moderado,
    percentual_critico=percentual_critico,
    horas_criticas=horas_criticas
)

st.sidebar.subheader("📅 Período de Análise")
data_inicio = st.sidebar.date_input("Data Início", value=datetime.today() - timedelta(days=7))
data_fim = st.sidebar.date_input("Data Fim", value=datetime.today())
num_dias = (data_fim - data_inicio).days + 1

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
    
    if dados_completos:
        return pd.concat(dados_completos, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Data", "Hora", "Gerado (kWh)", "Consumido (kWh)", "Excedente (kWh)"])

try:
    dados_historicos = gerar_dados_historicos(data_inicio, data_fim)
    dados_historicos['Data'] = pd.to_datetime(dados_historicos['Data'])
except Exception as e:
    st.error(f"Erro ao gerar dados históricos: {str(e)}")
    st.stop()

st.sidebar.subheader("🔍 Análise Detalhada")
try:
    datas_disponiveis = sorted(dados_historicos['Data'].dt.date.unique())
    data_selecionada = st.sidebar.selectbox("Selecionar Data", datas_disponiveis, index=len(datas_disponiveis)-1)
except Exception as e:
    st.error(f"Erro ao processar datas: {str(e)}")
    st.stop()

dados_dia = dados_historicos[dados_historicos['Data'].dt.date == data_selecionada].copy()

if not dados_dia.empty:
    try:
        analise_dia = sistema_alertas.analisar_excedente(dados_dia)
        notificacao_system.verificar_alertas_excedente(dados_dia)
    except Exception as e:
        st.error(f"Erro ao analisar dados: {str(e)}")
        analise_dia = None

tab1, tab2, tab3, tab4 = st.tabs(["🚨 Alertas do Dia", "📊 Visão Geral", "📈 Histórico", "⚙️ Configurações"])

with tab1:
    st.header(f"Alertas para {data_selecionada}")
    
    if not dados_dia.empty and analise_dia is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔋 Total Gerado", f"{dados_dia['Gerado (kWh)'].sum():.2f} kWh")
        with col2:
            st.metric("⚡ Total Consumido", f"{dados_dia['Consumido (kWh)'].sum():.2f} kWh")
        with col3:
            st.metric("➕ Excedente Total", f"{dados_dia['Excedente (kWh)'].sum():.2f} kWh")
        with col4:
            deficit_horas = len(dados_dia[dados_dia['Excedente (kWh)'] < 0])
            st.metric("⏰ Horas em Déficit", f"{deficit_horas}/24")
        
        sistema_alertas.exibir_alertas()
        
        st.subheader("📈 Excedente por Hora")
        
        fig = go.Figure()
        
        colors = ['red' if x < deficit_critico else 'orange' if x < 0 else 'green' for x in dados_dia['Excedente (kWh)']]
        
        fig.add_trace(go.Bar(
            x=dados_dia['Hora'].dt.strftime('%H:%M'),
            y=dados_dia['Excedente (kWh)'],
            marker_color=colors,
            name='Excedente'
        ))
        
        fig.add_hline(y=deficit_critico, line_dash="dash", line_color="red", 
                     annotation_text="Déficit Crítico")
        fig.add_hline(y=0, line_dash="dash", line_color="orange", 
                     annotation_text="Linha Zero")
        
        fig.update_layout(
            title="Excedente de Energia por Hora",
            xaxis_title="Hora",
            yaxis_title="Excedente (kWh)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        sistema_alertas.gerar_recomendacoes(analise_dia)
        
        st.subheader("📋 Dados Detalhados")
        
        dados_formatados = dados_dia[['Hora', 'Gerado (kWh)', 'Consumido (kWh)', 'Excedente (kWh)']].copy()
        
        dados_formatados['Hora'] = dados_formatados['Hora'].dt.strftime('%H:%M')
        
        def get_status(excedente):
            if excedente < deficit_critico:
                return "🔴 Crítico"
            elif excedente < 0:
                return "🟡 Déficit"
            else:
                return "🟢 Normal"
        
        dados_formatados['Status'] = dados_dia['Excedente (kWh)'].apply(get_status)
        
        dados_formatados = dados_formatados[['Hora', 'Status', 'Gerado (kWh)', 'Consumido (kWh)', 'Excedente (kWh)']]
        
        st.dataframe(
            dados_formatados,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("""
        **Legenda:**
        - 🔴 **Crítico**: Déficit maior que {} kWh
        - 🟡 **Déficit**: Consumo maior que produção
        - 🟢 **Normal**: Excedente positivo
        """.format(deficit_critico))
    elif dados_dia.empty:
        st.warning("Nenhum dado disponível para a data selecionada.")
    else:
        st.error("Erro ao processar os dados. Tente novamente ou selecione outra data.")

with tab2:
    st.header("📊 Visão Geral do Período")
    
    analise_diaria = []
    for data_unica in datas_disponiveis:
        try:
            dados_dia_temp = dados_historicos[dados_historicos['Data'].dt.date == data_unica].copy()
            if not dados_dia_temp.empty:
                analise_temp = sistema_alertas.analisar_excedente(dados_dia_temp)
                analise_temp['data'] = data_unica
                analise_diaria.append(analise_temp)
        except Exception as e:
            st.warning(f"Erro ao analisar dados para {data_unica}: {str(e)}")
            continue
    
    if analise_diaria:
        df_analise = pd.DataFrame(analise_diaria)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Tendência do Excedente")
            fig_tendencia = go.Figure()
            
            fig_tendencia.add_trace(go.Scatter(
                x=df_analise['data'],
                y=df_analise['excedente_total'],
                mode='lines+markers',
                name='Excedente Total',
                line=dict(color='blue', width=2)
            ))
            
            fig_tendencia.add_hline(y=0, line_dash="dash", line_color="red")
            fig_tendencia.update_layout(
                title="Excedente Total por Dia",
                xaxis_title="Data",
                yaxis_title="Excedente (kWh)",
                height=300
            )
            
            st.plotly_chart(fig_tendencia, use_container_width=True)
        
        with col2:
            st.subheader("⏰ Horas em Déficit")
            fig_deficit = go.Figure()
            
            fig_deficit.add_trace(go.Bar(
                x=df_analise['data'],
                y=df_analise['horas_deficit'],
                name='Horas em Déficit',
                marker_color='orange'
            ))
            
            fig_deficit.update_layout(
                title="Horas em Déficit por Dia",
                xaxis_title="Data",
                yaxis_title="Horas",
                height=300
            )
            
            st.plotly_chart(fig_deficit, use_container_width=True)
        
        st.subheader("📊 Estatísticas do Período")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            dias_deficit = len(df_analise[df_analise['excedente_total'] < 0])
            st.metric("🔴 Dias em Déficit", f"{dias_deficit}/{len(df_analise)}")
        
        with col2:
            media_excedente = df_analise['excedente_total'].mean()
            st.metric("📊 Média Excedente", f"{media_excedente:.2f} kWh")
        
        with col3:
            pior_dia = df_analise.loc[df_analise['excedente_total'].idxmin()]
            st.metric("📉 Pior Dia", f"{pior_dia['excedente_total']:.2f} kWh", 
                     delta=f"{pior_dia['data']}")
        
        with col4:
            melhor_dia = df_analise.loc[df_analise['excedente_total'].idxmax()]
            st.metric("📈 Melhor Dia", f"{melhor_dia['excedente_total']:.2f} kWh", 
                     delta=f"{melhor_dia['data']}")

with tab3:
    st.header("📈 Histórico de Alertas")
    
    alertas_periodo = []
    for data_unica in datas_disponiveis:
        dados_dia_temp = dados_historicos[dados_historicos['Data'].dt.date == data_unica].copy()
        if not dados_dia_temp.empty:
            sistema_temp = SistemaAlertas()
            sistema_temp.configurar_limites(
                deficit_critico=deficit_critico,
                deficit_moderado=deficit_moderado,
                percentual_critico=percentual_critico,
                horas_criticas=horas_criticas
            )
            sistema_temp.analisar_excedente(dados_dia_temp)
            
            for alerta in sistema_temp.alertas:
                alerta['data'] = data_unica
                alertas_periodo.append(alerta)
    
    if alertas_periodo:
        df_alertas = pd.DataFrame(alertas_periodo)
        
        st.subheader("🔢 Alertas por Tipo e Data")
        
        alertas_por_tipo = df_alertas.groupby(['data', 'tipo']).size().reset_index(name='count')
        
        fig_alertas = go.Figure()
        
        for tipo in ['critico', 'moderado', 'atencao']:
            dados_tipo = alertas_por_tipo[alertas_por_tipo['tipo'] == tipo]
            if not dados_tipo.empty:
                color = 'red' if tipo == 'critico' else 'orange' if tipo == 'moderado' else 'blue'
                fig_alertas.add_trace(go.Scatter(
                    x=dados_tipo['data'],
                    y=dados_tipo['count'],
                    mode='lines+markers',
                    name=tipo.capitalize(),
                    line=dict(color=color)
                ))
        
        fig_alertas.update_layout(
            title="Evolução dos Alertas",
            xaxis_title="Data",
            yaxis_title="Número de Alertas",
            height=400
        )
        
        st.plotly_chart(fig_alertas, use_container_width=True)
        
        st.subheader("📋 Lista de Alertas")
        
        col1, col2 = st.columns(2)
        with col1:
            tipos_selecionados = st.multiselect("Filtrar por Tipo", ['critico', 'moderado', 'atencao'], 
                                               default=['critico', 'moderado', 'atencao'])
        with col2:
            data_filtro = st.selectbox("Filtrar por Data", ['Todas'] + [str(d) for d in datas_disponiveis])
        
        df_filtrado = df_alertas[df_alertas['tipo'].isin(tipos_selecionados)]
        if data_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['data'].astype(str) == data_filtro]
        
        if not df_filtrado.empty:
            st.dataframe(
                df_filtrado[['data', 'tipo', 'mensagem', 'valor']].sort_values('data', ascending=False),
                use_container_width=True
            )
        else:
            st.info("Nenhum alerta encontrado com os filtros aplicados.")
        
        if st.button("📥 Exportar Histórico de Alertas"):
            csv = df_alertas.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"alertas_historico_{data_inicio}_{data_fim}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhum alerta gerado no período selecionado.")

with tab4:
    st.header("⚙️ Configurações Avançadas")
    
    st.subheader("🔔 Configurações de Notificação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Configurações Atuais:**")
        st.write(f"- Déficit Crítico: {deficit_critico} kWh")
        st.write(f"- Déficit Moderado: {deficit_moderado} kWh")
        st.write(f"- Percentual Crítico: {percentual_critico}%")
        st.write(f"- Horas Críticas: {horas_criticas}")
    
    with col2:
        st.write("**Ações Disponíveis:**")
        if st.button("🔄 Resetar Configurações"):
            st.rerun()
        
        if st.button("🗑️ Limpar Todas as Notificações"):
            st.session_state.notificacoes = []
            st.success("Notificações limpas!")

st.sidebar.divider()
notificacao_system.exibir_painel_notificacoes()
notificacao_system.auto_refresh_alertas()
notificacao_system.limpar_notificacoes_antigas()

stats = sistema_alertas.get_estatisticas()
if stats['total'] > 0:
    st.sidebar.subheader("📊 Estatísticas de Alertas")
    st.sidebar.write(f"**Total:** {stats['total']}")
    st.sidebar.write(f"**Críticos:** {stats['criticos']}")
    st.sidebar.write(f"**Moderados:** {stats['moderados']}")
    st.sidebar.write(f"**Atenção:** {stats['atencao']}")
    
    if st.sidebar.button("📋 Exportar Alertas Atuais"):
        alertas_df = sistema_alertas.exportar_alertas()
        if not alertas_df.empty:
            st.sidebar.dataframe(alertas_df)
        else:
            st.sidebar.info("Nenhum alerta para exportar") 