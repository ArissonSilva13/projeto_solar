import os
import sys
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from painel_admin.utils import (
    calcular_metricas_avancadas,
    gerar_dados_comparativo,
    gerar_dados_por_periodo,
    gerar_dados_relatorio,
)

if not st.session_state.get("logged_in"):
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

st.set_page_config(page_title="Relatórios", page_icon="📊", layout="wide")

st.title("📊 Relatórios e Análises")

with st.sidebar:
    st.header("⚙️ Configurações")
    
    periodo = st.selectbox(
        "📅 Período",
        ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"]
    )
    
    dias = 0
    if periodo == "Personalizado":
        data_inicio = st.date_input("Data início", value=datetime.now() - timedelta(days=7))
        data_fim = st.date_input("Data fim", value=datetime.now())
        if data_inicio and data_fim:
            dias = (data_fim - data_inicio).days
    else:
        dias = {"Últimos 7 dias": 7, "Últimos 30 dias": 30, "Últimos 90 dias": 90}[periodo]
    
    tipo_relatorio = st.selectbox(
        "📋 Tipo de Relatório",
        ["Resumo Geral", "Análise Detalhada", "Comparativo Mensal", "Eficiência e Performance"]
    )
    
    mostrar_graficos = st.checkbox("📈 Mostrar Gráficos Interativos", value=True)
    mostrar_metricas = st.checkbox("📊 Mostrar Métricas Avançadas", value=True)
    
    if st.button("🔄 Gerar Relatório", type="primary"):
        st.session_state.relatorio_gerado = True
        st.session_state.dias_relatorio = dias
        st.session_state.tipo_relatorio = tipo_relatorio
        st.session_state.mostrar_graficos = mostrar_graficos
        st.session_state.mostrar_metricas = mostrar_metricas

def exportar_dados(df, formato="csv"):
    if formato == "csv":
        return df.to_csv(index=False).encode('utf-8')
    elif formato == "excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Relatório', index=False)
        return output.getvalue()

def renderizar_graficos(df, tipo_relatorio):
    
    if tipo_relatorio == "Resumo Geral":
        fig1 = px.line(df, x='Data', y=['Gerado (kWh)', 'Consumido (kWh)'], 
                      title='Produção vs Consumo ao Longo do Tempo',
                      labels={'value': 'Energia (kWh)', 'variable': 'Tipo'})
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.bar(df, x='Data', y='Excedente (kWh)', 
                     title='Excedente Diário de Energia',
                     color='Excedente (kWh)', 
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig2, use_container_width=True)
    
    elif tipo_relatorio == "Análise Detalhada":
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df['Data'], y=df['Gerado (kWh)'], 
                                 fill='tonexty', name='Gerado'))
        fig1.add_trace(go.Scatter(x=df['Data'], y=df['Consumido (kWh)'], 
                                 fill='tozeroy', name='Consumido'))
        fig1.update_layout(title='Análise Detalhada de Produção e Consumo')
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.scatter(df, x='Data', y='Eficiencia (%)', 
                         size='Gerado (kWh)', color='Excedente (kWh)',
                         title='Eficiência do Sistema Solar')
        st.plotly_chart(fig2, use_container_width=True)
        
        df_semana = df.groupby('Dia_Semana').agg({
            'Gerado (kWh)': 'mean',
            'Consumido (kWh)': 'mean',
            'Eficiencia (%)': 'mean'
        }).round(2)
        
        fig3 = px.bar(df_semana, x=df_semana.index, y=['Gerado (kWh)', 'Consumido (kWh)'],
                     title='Média de Produção e Consumo por Dia da Semana',
                     barmode='group')
        st.plotly_chart(fig3, use_container_width=True)
    
    elif tipo_relatorio == "Eficiência e Performance":
        eficiencia_media = df['Eficiencia (%)'].mean()
        fig1 = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = eficiencia_media,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Eficiência Média (%)"},
            delta = {'reference': 75},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "yellow"},
                        {'range': [75, 100], 'color': "green"}],
                    'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': 90}}))
        st.plotly_chart(fig1, use_container_width=True)
        
        df['Semana'] = pd.to_datetime(df['Data']).dt.isocalendar().week
        df_heatmap = df.pivot_table(values='Gerado (kWh)', index='Semana', columns='Dia_Semana', aggfunc='mean')
        
        fig2 = px.imshow(df_heatmap.values, 
                        labels=dict(x="Dia da Semana", y="Semana", color="Gerado (kWh)"),
                        x=df_heatmap.columns, y=df_heatmap.index,
                        title="Heatmap de Produção por Semana e Dia")
        st.plotly_chart(fig2, use_container_width=True)

def renderizar_relatorio_comparativo():
    df_comparativo = gerar_dados_por_periodo("mensal", 12)
    
    fig = px.bar(df_comparativo, x='Periodo', y=['Gerado (kWh)', 'Consumido (kWh)'],
                title='Comparativo Mensal - Produção vs Consumo',
                barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    fig2 = px.line(df_comparativo, x='Periodo', y='Economia (R$)',
                  title='Evolução da Economia Mensal',
                  markers=True)
    st.plotly_chart(fig2, use_container_width=True)
    
    return df_comparativo

if st.session_state.get("relatorio_gerado", False):
    dias_relatorio = st.session_state.get("dias_relatorio", 30)
    tipo_relatorio = st.session_state.get("tipo_relatorio", "Resumo Geral")
    mostrar_graficos = st.session_state.get("mostrar_graficos", True)
    mostrar_metricas = st.session_state.get("mostrar_metricas", True)
    
    if tipo_relatorio == "Comparativo Mensal":
        df_relatorio = renderizar_relatorio_comparativo()
    else:
        df_relatorio = gerar_dados_relatorio(dias_relatorio)
    
    st.header(f"📊 {tipo_relatorio}")
    st.caption(f"Período: {periodo} | Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    if mostrar_metricas and tipo_relatorio != "Comparativo Mensal":
        metricas = calcular_metricas_avancadas(df_relatorio)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Gerado", f"{metricas['total_gerado']:.1f} kWh", 
                     f"{metricas['media_diaria_gerada']:.1f} kWh/dia")
        with col2:
            st.metric("Total Consumido", f"{metricas['total_consumido']:.1f} kWh", 
                     f"{metricas['media_diaria_consumida']:.1f} kWh/dia")
        with col3:
            st.metric("Excedente Total", f"{metricas['total_excedente']:.1f} kWh", 
                     f"{metricas['percentual_excedente']:.1f}% dos dias")
        with col4:
            st.metric("Eficiência Média", f"{metricas['eficiencia_media']:.1f}%")
        
        st.subheader("📈 Análise Detalhada")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Melhor dia:** {metricas['melhor_dia']}")
        with col2:
            st.info(f"**Pior dia:** {metricas['pior_dia']}")
        with col3:
            st.info(f"**Dias com excedente:** {metricas['dias_com_excedente']}")
    
    if mostrar_graficos:
        st.subheader("📈 Visualizações")
        if tipo_relatorio != "Comparativo Mensal":
            renderizar_graficos(df_relatorio, tipo_relatorio)
    
    st.subheader("📋 Dados Detalhados")
    st.dataframe(df_relatorio, use_container_width=True)
    
    st.subheader("💾 Exportar Dados")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Exportar CSV"):
            csv = exportar_dados(df_relatorio, "csv")
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"relatorio_{tipo_relatorio.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    with col2:
        if st.button("📊 Exportar Excel"):
            excel = exportar_dados(df_relatorio, "excel")
            st.download_button(
                label="⬇️ Download Excel",
                data=excel,
                file_name=f"relatorio_{tipo_relatorio.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("👈 Configure as opções na barra lateral e clique em 'Gerar Relatório' para visualizar os dados.")
    
    st.subheader("📋 Tipos de Relatório Disponíveis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **📊 Resumo Geral**
        - Métricas principais
        - Gráficos de linha e barras
        - Visão geral da produção e consumo
        """)
        
        st.info("""
        **🔍 Análise Detalhada**
        - Gráficos de área empilhada
        - Análise de eficiência
        - Produção por dia da semana
        """)
    
    with col2:
        st.info("""
        **📈 Comparativo Mensal**
        - Comparação entre meses
        - Evolução da economia
        - Tendências históricas
        """)
        
        st.info("""
        **⚡ Eficiência e Performance**
        - Gauge de eficiência
        - Heatmap de produção
        - Análise de performance
        """) 