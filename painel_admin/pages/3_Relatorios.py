import os
import sys
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Importa o estilo global
from shared import aplicar_estilo_solar

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Mantemos suas importações originais
from painel_admin.utils import (
    calcular_metricas_avancadas,
    gerar_dados_comparativo,
    gerar_dados_por_periodo,
    gerar_dados_relatorio,
)

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Relatórios & BI", page_icon="📈", layout="wide")
aplicar_estilo_solar()

# --- HELPER PARA ÍCONES SVG ---
def render_icon(svg_path, title, color="#1E3A8A"):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            {svg_path}
        </svg>
        <h4 style="margin: 0; color: #1E3A8A; font-weight: 600; font-family: sans-serif;">{title}</h4>
    </div>
    """, unsafe_allow_html=True)

# Paleta de Cores da Marca
CORES = {
    "gerado": "#FF8C00",    # Laranja
    "consumido": "#1E3A8A", # Azul Escuro
    "excedente": "#10B981", # Verde
    "fundo": "#FFFFFF"
}

if not st.session_state.get("logged_in"):
    st.error("🔒 Acesso restrito. Faça login.")
    st.stop()

# Título Limpo
st.title("Business Intelligence")
st.markdown("Análise detalhada de performance, tendências energéticas e dados históricos.")

# --- SIDEBAR (LIMPA) ---
with st.sidebar:
    st.header("Filtros de Análise")
    
    # SVG: Calendar
    render_icon('<rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>', "Período", "#FF8C00")
    
    periodo = st.selectbox(
        "Selecione o Intervalo",
        ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"],
        label_visibility="collapsed"
    )
    
    dias = 0
    if periodo == "Personalizado":
        col_d1, col_d2 = st.columns(2)
        data_inicio = col_d1.date_input("Início", value=datetime.now() - timedelta(days=7))
        data_fim = col_d2.date_input("Fim", value=datetime.now())
        if data_inicio and data_fim:
            dias = (data_fim - data_inicio).days
    else:
        dias = {"Últimos 7 dias": 7, "Últimos 30 dias": 30, "Últimos 90 dias": 90}[periodo]
    
    st.markdown("---")
    
    # SVG: Layers/Tipo
    render_icon('<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline>', "Tipo de Relatório", "#1E3A8A")
    
    tipo_relatorio = st.selectbox(
        "Selecione a Visão",
        ["Resumo Geral", "Análise Detalhada", "Comparativo Mensal", "Eficiência e Performance"],
        label_visibility="collapsed"
    )
    
    with st.expander("Configurações de Visualização"):
        mostrar_graficos = st.checkbox("Exibir Gráficos", value=True)
        mostrar_metricas = st.checkbox("Exibir KPIs", value=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Atualizar Dashboard", type="primary", use_container_width=True):
        st.session_state.relatorio_gerado = True
        st.session_state.dias_relatorio = dias
        st.session_state.tipo_relatorio = tipo_relatorio
        st.session_state.mostrar_graficos = mostrar_graficos
        st.session_state.mostrar_metricas = mostrar_metricas

# --- FUNÇÕES AUXILIARES ---
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
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            render_icon('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>', "Produção vs Consumo")
            fig1 = px.area(df, x='Data', y=['Gerado (kWh)', 'Consumido (kWh)'], 
                          color_discrete_map={'Gerado (kWh)': CORES['gerado'], 'Consumido (kWh)': CORES['consumido']},
                          labels={'value': 'Energia (kWh)', 'variable': 'Métrica'})
            fig1.update_layout(legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig1, use_container_width=True)
        with col_g2:
            render_icon('<rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>', "Excedente Diário")
            fig2 = px.bar(df, x='Data', y='Excedente (kWh)', 
                         color='Excedente (kWh)',
                         color_continuous_scale='Mint')
            fig2.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)
    
    elif tipo_relatorio == "Análise Detalhada":
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df['Data'], y=df['Gerado (kWh)'], 
                                 fill='tonexty', name='Gerado', line=dict(color=CORES['gerado'])))
        fig1.add_trace(go.Scatter(x=df['Data'], y=df['Consumido (kWh)'], 
                                 fill='tozeroy', name='Consumido', line=dict(color=CORES['consumido'])))
        fig1.update_layout(title='Curva de Carga Detalhada', hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.scatter(df, x='Data', y='Eficiencia (%)', 
                             size='Gerado (kWh)', color='Excedente (kWh)',
                             title='Eficiência vs Geração (Dispersão)', color_continuous_scale='Oranges')
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            df_semana = df.groupby('Dia_Semana').agg({
                'Gerado (kWh)': 'mean', 'Consumido (kWh)': 'mean', 'Eficiencia (%)': 'mean'
            }).round(2)
            fig3 = px.bar(df_semana, x=df_semana.index, y=['Gerado (kWh)', 'Consumido (kWh)'],
                          title='Perfil Semanal Médio', barmode='group',
                          color_discrete_map={'Gerado (kWh)': CORES['gerado'], 'Consumido (kWh)': CORES['consumido']})
            st.plotly_chart(fig3, use_container_width=True)
    
    elif tipo_relatorio == "Eficiência e Performance":
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            eficiencia_media = df['Eficiencia (%)'].mean()
            fig1 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = eficiencia_media,
                title = {'text': "Eficiência Média"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': CORES['gerado']},
                    'steps': [
                        {'range': [0, 50], 'color': "#F3F4F6"},
                        {'range': [50, 80], 'color': "#E5E7EB"},
                        {'range': [80, 100], 'color': "#D1FAE5"}]
                }))
            st.plotly_chart(fig1, use_container_width=True)
        with col_g2:
            df['Semana'] = pd.to_datetime(df['Data']).dt.isocalendar().week
            df_heatmap = df.pivot_table(values='Gerado (kWh)', index='Semana', columns='Dia_Semana', aggfunc='mean')
            fig2 = px.imshow(df_heatmap.values, 
                            labels=dict(x="Dia", y="Semana", color="kWh"),
                            x=df_heatmap.columns, y=df_heatmap.index,
                            title="Mapa de Calor de Produção Solar",
                            color_continuous_scale='Solar')
            st.plotly_chart(fig2, use_container_width=True)

    elif tipo_relatorio == "Comparativo Mensal":
        # Gráfico de Barras Comparativo
        fig = px.bar(df, x='Periodo', y=['Gerado (kWh)', 'Consumido (kWh)'],
                    title='Comparativo Mensal (Últimos 12 Meses)',
                    barmode='group',
                    color_discrete_map={'Gerado (kWh)': CORES['gerado'], 'Consumido (kWh)': CORES['consumido']})
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de Linha Financeiro
        fig2 = px.line(df, x='Periodo', y='Economia (R$)',
                    title='Evolução Financeira da Economia',
                    markers=True, line_shape='spline')
        fig2.update_traces(line_color=CORES['excedente'], line_width=4)
        st.plotly_chart(fig2, use_container_width=True)

# --- LÓGICA PRINCIPAL ---
if st.session_state.get("relatorio_gerado", False):
    dias_relatorio = st.session_state.get("dias_relatorio", 30)
    tipo_relatorio = st.session_state.get("tipo_relatorio", "Resumo Geral")
    mostrar_graficos = st.session_state.get("mostrar_graficos", True)
    mostrar_metricas = st.session_state.get("mostrar_metricas", True)
    
    # Busca os dados (sem exibir gráficos ainda)
    if tipo_relatorio == "Comparativo Mensal":
        df_relatorio = gerar_dados_por_periodo("mensal", 12)
    else:
        df_relatorio = gerar_dados_relatorio(dias_relatorio)
    
    # --- PADRONIZAÇÃO DE COLUNAS (BLINDAGEM) ---
    if df_relatorio is not None and not df_relatorio.empty:
        col_map = {
            'producao_kwh': 'Gerado (kWh)', 'consumo_kwh': 'Consumido (kWh)',
            'injetado_kwh': 'Excedente (kWh)', 'economia_reais': 'Economia (R$)',
            'gerado': 'Gerado (kWh)', 'consumido': 'Consumido (kWh)',
            'excedente': 'Excedente (kWh)', 'eficiencia': 'Eficiencia (%)', 'data': 'Data'
        }
        new_cols = []
        for col in df_relatorio.columns:
            clean_col = str(col).lower().strip()
            new_cols.append(col_map.get(clean_col, col))
        df_relatorio.columns = new_cols
        
        if 'Eficiencia (%)' not in df_relatorio.columns:
            if 'Gerado (kWh)' in df_relatorio.columns:
                max_prod = df_relatorio['Gerado (kWh)'].max()
                df_relatorio['Eficiencia (%)'] = (df_relatorio['Gerado (kWh)'] / max_prod * 100) if max_prod > 0 else 0
        
        if 'Economia (R$)' not in df_relatorio.columns:
             df_relatorio['Economia (R$)'] = 0.0

        if 'Data' in df_relatorio.columns and 'Dia_Semana' not in df_relatorio.columns:
             try:
                df_relatorio['Data'] = pd.to_datetime(df_relatorio['Data'])
                df_relatorio['Dia_Semana'] = df_relatorio['Data'].dt.day_name()
             except: pass

    st.markdown("---")
    # SVG: File Text
    render_icon('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>', 
                f"{tipo_relatorio} - Resultados")
    
    st.caption(f"Dados consolidados em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    
    # 1. KPIs
    if mostrar_metricas and tipo_relatorio != "Comparativo Mensal":
        metricas = calcular_metricas_avancadas(df_relatorio)
        
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)
            # Labels limpos
            col1.metric("Total Gerado", f"{metricas['total_gerado']:.1f} kWh", f"Média: {metricas['media_diaria_gerada']:.1f}")
            col2.metric("Total Consumido", f"{metricas['total_consumido']:.1f} kWh", f"Média: {metricas['media_diaria_consumida']:.1f}")
            col3.metric("Saldo Excedente", f"{metricas['total_excedente']:.1f} kWh", f"Sobra: {metricas['percentual_excedente']:.1f}%")
            col4.metric("Eficiência Global", f"{metricas['eficiencia_media']:.1f}%", "Sistema")
        
        # Insights (usando st.success/info limpos)
        c1, c2, c3 = st.columns(3)
        c1.success(f"Melhor Dia: {metricas['melhor_dia']}")
        c2.warning(f"Pior Dia: {metricas['pior_dia']}")
        c3.info(f"Dias Positivos: {metricas['dias_com_excedente']} dias")
    
    # 2. GRÁFICOS (Agora inclui o Comparativo Mensal aqui dentro)
    if mostrar_graficos:
        st.markdown("<br>", unsafe_allow_html=True)
        render_icon('<rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect>', "Dashboard Interativo")
        
        # Chama a função de renderização correta
        renderizar_graficos(df_relatorio, tipo_relatorio)
    
    # 3. TABELA
    st.markdown("<br>", unsafe_allow_html=True)
    render_icon('<line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line>', "Base de Dados")
    
    with st.expander("Visualizar dados em tabela", expanded=True):
        # Ajuste de colunas para tabelas mensais (que não têm 'Data')
        col_config = {
            "Gerado (kWh)": st.column_config.ProgressColumn(
                "Geração", format="%.2f kWh", min_value=0, max_value=float(df_relatorio.get("Gerado (kWh)", 100).max())
            ),
            "Consumido (kWh)": st.column_config.NumberColumn("Consumo", format="%.2f kWh"),
            "Eficiencia (%)": st.column_config.ProgressColumn("Eficiência", format="%.1f%%", min_value=0, max_value=100),
            "Economia (R$)": st.column_config.NumberColumn("Economia", format="R$ %.2f")
        }
        
        if "Data" in df_relatorio.columns:
            col_config["Data"] = st.column_config.DateColumn("Data", format="DD/MM/YYYY")
            
        st.dataframe(
            df_relatorio, 
            use_container_width=True,
            column_config=col_config
        )
    
    # 4. DOWNLOAD
    st.markdown("<br>", unsafe_allow_html=True)
    render_icon('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line>', "Exportação")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        csv = exportar_dados(df_relatorio, "csv")
        st.download_button("Baixar CSV", data=csv, file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
    with col2:
        excel = exportar_dados(df_relatorio, "excel")
        st.download_button("Baixar Excel", data=excel, file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

else:
    # Estado inicial clean
    st.info("Utilize o menu lateral para configurar o período e clique em 'Atualizar Dashboard'.")
    
    # Placeholder visual (Logo cinza)
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown("""
        <div style="text-align: center; opacity: 0.5; margin-top: 50px;">
            <h1 style="color: #ccc; font-size: 50px;">📊</h1>
            <p>Aguardando filtros...</p>
        </div>
        """, unsafe_allow_html=True)