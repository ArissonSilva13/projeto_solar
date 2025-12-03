import os
import sys
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Importa o estilo global que criamos
from shared import aplicar_estilo_solar

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Mantemos suas importações originais intactas
from painel_admin.utils import (
    calcular_metricas_avancadas,
    gerar_dados_comparativo,
    gerar_dados_por_periodo,
    gerar_dados_relatorio,
)

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Relatórios Avançados", page_icon="📊", layout="wide")
aplicar_estilo_solar() # <--- APLICA O CSS AQUI

# Paleta de Cores da Marca (Para consistência nos gráficos)
CORES = {
    "gerado": "#FF8C00",    # Laranja
    "consumido": "#1E3A8A", # Azul Escuro
    "excedente": "#10B981", # Verde
    "fundo": "#FFFFFF"
}

if not st.session_state.get("logged_in"):
    st.warning("🔒 Você precisa estar logado para acessar esta página.")
    st.stop()

st.title("📊 Relatórios e Business Intelligence")
st.markdown("Gere relatórios detalhados, analise tendências e exporte dados do seu sistema.")

# --- SIDEBAR (MANTIDA IGUAL, APENAS CLEANER) ---
with st.sidebar:
    st.header("⚙️ Configuração do Relatório")
    
    periodo = st.selectbox(
        "📅 Período de Análise",
        ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"]
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
    
    st.divider()
    
    tipo_relatorio = st.selectbox(
        "📋 Tipo de Análise",
        ["Resumo Geral", "Análise Detalhada", "Comparativo Mensal", "Eficiência e Performance"]
    )
    
    with st.expander("Opções de Visualização"):
        mostrar_graficos = st.checkbox("📈 Gráficos Interativos", value=True)
        mostrar_metricas = st.checkbox("📊 Cards de Métricas", value=True)
    
    st.divider()
    
    if st.button("🔄 Gerar Relatório Agora", type="primary", use_container_width=True):
        st.session_state.relatorio_gerado = True
        st.session_state.dias_relatorio = dias
        st.session_state.tipo_relatorio = tipo_relatorio
        st.session_state.mostrar_graficos = mostrar_graficos
        st.session_state.mostrar_metricas = mostrar_metricas

# --- FUNÇÕES AUXILIARES (VISUAL MELHORADO) ---
def exportar_dados(df, formato="csv"):
    if formato == "csv":
        return df.to_csv(index=False).encode('utf-8')
    elif formato == "excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Relatório', index=False)
        return output.getvalue()

def renderizar_graficos(df, tipo_relatorio):
    # Aqui aplicamos as CORES da marca nos gráficos
    
    if tipo_relatorio == "Resumo Geral":
        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            st.markdown("##### Produção vs Consumo")
            fig1 = px.area(df, x='Data', y=['Gerado (kWh)', 'Consumido (kWh)'], 
                          color_discrete_map={'Gerado (kWh)': CORES['gerado'], 'Consumido (kWh)': CORES['consumido']},
                          labels={'value': 'Energia (kWh)', 'variable': 'Métrica'})
            fig1.update_layout(legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_g2:
            st.markdown("##### Excedente Diário")
            fig2 = px.bar(df, x='Data', y='Excedente (kWh)', 
                         color='Excedente (kWh)',
                         color_continuous_scale='Mint') # Escala verde profissional
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
            # Gráfico de Dispersão Melhorado
            fig2 = px.scatter(df, x='Data', y='Eficiencia (%)', 
                             size='Gerado (kWh)', color='Excedente (kWh)',
                             title='Eficiência vs Geração (Bolhas)', color_continuous_scale='Oranges')
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            # Agrupamento
            df_semana = df.groupby('Dia_Semana').agg({
                'Gerado (kWh)': 'mean',
                'Consumido (kWh)': 'mean',
                'Eficiencia (%)': 'mean'
            }).round(2)
            
            fig3 = px.bar(df_semana, x=df_semana.index, y=['Gerado (kWh)', 'Consumido (kWh)'],
                          title='Perfil Semanal', barmode='group',
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
            # Heatmap com cores melhores
            df['Semana'] = pd.to_datetime(df['Data']).dt.isocalendar().week
            df_heatmap = df.pivot_table(values='Gerado (kWh)', index='Semana', columns='Dia_Semana', aggfunc='mean')
            
            fig2 = px.imshow(df_heatmap.values, 
                            labels=dict(x="Dia", y="Semana", color="kWh"),
                            x=df_heatmap.columns, y=df_heatmap.index,
                            title="Mapa de Calor de Produção Solar",
                            color_continuous_scale='Solar') # Escala quente
            st.plotly_chart(fig2, use_container_width=True)

def renderizar_relatorio_comparativo():
    df_comparativo = gerar_dados_por_periodo("mensal", 12)
    
    fig = px.bar(df_comparativo, x='Periodo', y=['Gerado (kWh)', 'Consumido (kWh)'],
                title='Comparativo Mensal (Últimos 12 Meses)',
                barmode='group',
                color_discrete_map={'Gerado (kWh)': CORES['gerado'], 'Consumido (kWh)': CORES['consumido']})
    st.plotly_chart(fig, use_container_width=True)
    
    # Linha de Tendência Financeira
    fig2 = px.line(df_comparativo, x='Periodo', y='Economia (R$)',
                  title='Evolução Financeira da Economia',
                  markers=True, line_shape='spline')
    fig2.update_traces(line_color=CORES['excedente'], line_width=4)
    st.plotly_chart(fig2, use_container_width=True)
    
    return df_comparativo

# --- LÓGICA PRINCIPAL ---
if st.session_state.get("relatorio_gerado", False):
    # Recupera variáveis do estado
    dias_relatorio = st.session_state.get("dias_relatorio", 30)
    tipo_relatorio = st.session_state.get("tipo_relatorio", "Resumo Geral")
    mostrar_graficos = st.session_state.get("mostrar_graficos", True)
    mostrar_metricas = st.session_state.get("mostrar_metricas", True)
    
    # Gera os dados (Mantendo sua lógica original)
    if tipo_relatorio == "Comparativo Mensal":
        df_relatorio = renderizar_relatorio_comparativo()
    else:
        df_relatorio = gerar_dados_relatorio(dias_relatorio)
    
    # --- CORREÇÃO DE ERRO: PADRONIZAÇÃO DE COLUNAS V3 (FINAL) ---
    # Garante que as colunas existam mesmo se vierem com nomes diferentes do utils
    if df_relatorio is not None and not df_relatorio.empty:
        # Mapa exato baseado no seu print de erro
        col_map = {
            # Mapeamento Direto do seu Banco (Baseado no Print)
            'producao_kwh': 'Gerado (kWh)',
            'consumo_kwh': 'Consumido (kWh)',
            'injetado_kwh': 'Excedente (kWh)',
            'economia_reais': 'Economia (R$)',
            
            # Variações extras por segurança
            'gerado': 'Gerado (kWh)', 
            'consumido': 'Consumido (kWh)',
            'excedente': 'Excedente (kWh)',
            'eficiencia': 'Eficiencia (%)',
            'data': 'Data'
        }
        
        # 1. Renomeia as colunas
        new_cols = []
        for col in df_relatorio.columns:
            clean_col = str(col).lower().strip()
            new_name = col_map.get(clean_col, col) # Usa o nome mapeado ou o original
            new_cols.append(new_name)
        
        df_relatorio.columns = new_cols
        
        # 2. Garante que Eficiência exista (Calcula se faltar)
        if 'Eficiencia (%)' not in df_relatorio.columns:
            if 'Gerado (kWh)' in df_relatorio.columns:
                # Cria uma eficiência estimada baseada na produção relativa ao máximo do período
                # Isso evita que o gráfico de eficiência quebre
                max_prod = df_relatorio['Gerado (kWh)'].max()
                if max_prod > 0:
                    df_relatorio['Eficiencia (%)'] = (df_relatorio['Gerado (kWh)'] / max_prod) * 100
                else:
                    df_relatorio['Eficiencia (%)'] = 0
        
        # 3. Garante que Economia exista
        if 'Economia (R$)' not in df_relatorio.columns:
             df_relatorio['Economia (R$)'] = 0.0

        # 4. Verificação Final de Segurança
        required_cols = ['Gerado (kWh)', 'Consumido (kWh)', 'Excedente (kWh)']
        missing = [c for c in required_cols if c not in df_relatorio.columns]
        
        if missing:
            st.error("⚠️ Estrutura de dados incompatível detectada.")
            st.write(f"Esperávamos colunas como: {required_cols}")
            st.write(f"Mas recebemos estas colunas (após tentativa de correção): {list(df_relatorio.columns)}")
            st.stop()
            
        # Adiciona coluna Dia_Semana se não existir (necessário para gráficos detalhados)
        if 'Data' in df_relatorio.columns and 'Dia_Semana' not in df_relatorio.columns:
             try:
                df_relatorio['Data'] = pd.to_datetime(df_relatorio['Data'])
                df_relatorio['Dia_Semana'] = df_relatorio['Data'].dt.day_name()
             except:
                pass
    # ---------------------------------------------------

    st.markdown("---")
    st.subheader(f"📑 {tipo_relatorio}")
    st.caption(f"Dados gerados em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    
    # 1. VISUALIZAÇÃO DE MÉTRICAS (Agora dentro de container estilizado)
    if mostrar_metricas and tipo_relatorio != "Comparativo Mensal":
        # Chama a função original que estava dando erro
        metricas = calcular_metricas_avancadas(df_relatorio)
        
        with st.container(border=True): # <--- Borda bonita em volta
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("☀️ Total Gerado", f"{metricas['total_gerado']:.1f} kWh", 
                       f"Média: {metricas['media_diaria_gerada']:.1f} kWh")
            col2.metric("🏠 Total Consumido", f"{metricas['total_consumido']:.1f} kWh", 
                       f"Média: {metricas['media_diaria_consumida']:.1f} kWh")
            col3.metric("🔋 Excedente", f"{metricas['total_excedente']:.1f} kWh", 
                       f"Sobra: {metricas['percentual_excedente']:.1f}%")
            col4.metric("⚡ Eficiência Global", f"{metricas['eficiencia_media']:.1f}%", "Sistema")
        
        # Insights em caixas coloridas
        c1, c2, c3 = st.columns(3)
        c1.success(f"🏆 **Melhor Dia:** {metricas['melhor_dia']}")
        c2.error(f"⚠️ **Pior Dia:** {metricas['pior_dia']}")
        c3.info(f"📅 **Dias Positivos:** {metricas['dias_com_excedente']} dias com sobra")
    
    # 2. VISUALIZAÇÃO DE GRÁFICOS
    if mostrar_graficos:
        st.markdown("### 📈 Dashboard Interativo")
        if tipo_relatorio != "Comparativo Mensal":
            renderizar_graficos(df_relatorio, tipo_relatorio)
    
    # 3. TABELA DETALHADA (Agora com Column Config)
    st.markdown("### 📋 Base de Dados")
    with st.expander("Ver dados brutos em tabela", expanded=True):
        # Configuração avançada de colunas para ficar visualmente rico
        st.dataframe(
            df_relatorio, 
            use_container_width=True,
            column_config={
                "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "Gerado (kWh)": st.column_config.ProgressColumn(
                    "Geração Solar", format="%.2f kWh", min_value=0, max_value=float(df_relatorio.get("Gerado (kWh)", 100).max())
                ),
                "Consumido (kWh)": st.column_config.NumberColumn(
                    "Consumo", format="%.2f kWh"
                ),
                "Eficiencia (%)": st.column_config.ProgressColumn(
                    "Eficiência", format="%.1f%%", min_value=0, max_value=100
                ),
                "Economia (R$)": st.column_config.NumberColumn(
                    "Economia", format="R$ %.2f"
                )
            }
        )
    
    # 4. ÁREA DE EXPORTAÇÃO
    st.markdown("### 💾 Download")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        csv = exportar_dados(df_relatorio, "csv")
        st.download_button(
            label="📄 Baixar CSV",
            data=csv,
            file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        excel = exportar_dados(df_relatorio, "excel")
        st.download_button(
            label="📊 Baixar Excel",
            data=excel,
            file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    # Estado inicial (sem relatório gerado)
    st.info("👈 Utilize o menu lateral para configurar o período e clique em **'Gerar Relatório Agora'**.")
    
    # Mostra um preview estático bonito só para não ficar vazio
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=50)
    st.markdown("### Selecione uma das opções:")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        * **Resumo Geral:** Visão macro da energia.
        * **Análise Detalhada:** Gráficos dia a dia.
        """)
    with c2:
        st.markdown("""
        * **Comparativo Mensal:** Evolução anual.
        * **Performance:** Análise técnica do inversor.
        """)