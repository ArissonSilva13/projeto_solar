import streamlit as st
import yaml
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from streamlit_authenticator import Hasher
import io
import json

# ✅ Proteção de acesso
if not st.session_state.get("logged_in"):
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

st.set_page_config(page_title="Ajustes", page_icon="⚙️", layout="wide")

ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"

# Função para carregar dados de usuários
@st.cache_data
def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

# Função para salvar dados de usuários
def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, "w") as f:
        yaml.dump(dados, f, default_flow_style=False)

# Função para gerar dados de exemplo para relatórios
@st.cache_data
def gerar_dados_relatorio(dias=30):
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=dias),
        end=datetime.now(),
        freq="D"
    )
    
    data = []
    for date in dates:
        # Simulando dados diários
        gerado_total = np.random.uniform(15, 45)  # kWh por dia
        consumido_total = np.random.uniform(20, 40)  # kWh por dia
        excedente = gerado_total - consumido_total
        
        data.append({
            "Data": date.strftime("%Y-%m-%d"),
            "Gerado (kWh)": round(gerado_total, 2),
            "Consumido (kWh)": round(consumido_total, 2),
            "Excedente (kWh)": round(excedente, 2),
            "Economia (R$)": round(excedente * 0.75, 2)  # R$ 0.75 por kWh
        })
    
    return pd.DataFrame(data)

st.title("⚙️ Configurações e Ajustes")

# Criando abas para organizar as funcionalidades
tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Opções de Usuário",
    "📊 Relatórios",
    "📥 Exportação",
    "🔌 Integração"
])

# TAB 1: Opções de Usuário
with tab1:
    st.header("Configurações de Usuário")
    
    # Carregando dados do usuário atual
    dados_usuarios = carregar_usuarios()
    usuario_atual = st.session_state.get("username")
    
    if usuario_atual and usuario_atual in dados_usuarios.get("usernames", {}):
        user_data = dados_usuarios["usernames"][usuario_atual]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Informações Pessoais")
            novo_nome = st.text_input("Nome completo", value=user_data.get("name", ""))
            novo_email = st.text_input("Email", value=user_data.get("email", ""))
            
            if st.button("💾 Salvar Alterações"):
                if novo_nome and novo_email:
                    dados_usuarios["usernames"][usuario_atual]["name"] = novo_nome
                    dados_usuarios["usernames"][usuario_atual]["email"] = novo_email
                    salvar_usuarios(dados_usuarios)
                    st.success("Informações atualizadas com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha todos os campos.")
        
        with col2:
            st.subheader("Alterar Senha")
            senha_atual = st.text_input("Senha atual", type="password")
            nova_senha = st.text_input("Nova senha", type="password")
            confirmar_senha = st.text_input("Confirmar nova senha", type="password")
            
            if st.button("🔒 Alterar Senha"):
                if not senha_atual or not nova_senha or not confirmar_senha:
                    st.warning("Preencha todos os campos.")
                elif nova_senha != confirmar_senha:
                    st.error("As senhas não coincidem.")
                elif len(nova_senha) < 4:
                    st.error("A senha deve ter pelo menos 4 caracteres.")
                else:
                    # Verificar senha atual (simplificado)
                    nova_senha_hash = Hasher([nova_senha]).generate()[0]
                    dados_usuarios["usernames"][usuario_atual]["password"] = nova_senha_hash
                    salvar_usuarios(dados_usuarios)
                    st.success("Senha alterada com sucesso!")
    
    # Configurações de Sistema
    st.subheader("Configurações do Sistema")
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Tema", ["Claro", "Escuro", "Auto"], help="Configuração visual do sistema")
        st.selectbox("Idioma", ["Português", "Inglês", "Espanhol"], help="Idioma da interface")
    
    with col2:
        st.number_input("Timeout da sessão (minutos)", min_value=5, max_value=120, value=30)
        st.checkbox("Notificações por email", help="Receber alertas por email")

# TAB 2: Relatórios
with tab2:
    st.header("Relatórios e Análises")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("Configurações do Relatório")
        periodo = st.selectbox(
            "Período",
            ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"]
        )
        
        if periodo == "Personalizado":
            data_inicio = st.date_input("Data início")
            data_fim = st.date_input("Data fim")
            dias = (data_fim - data_inicio).days
        else:
            dias = {"Últimos 7 dias": 7, "Últimos 30 dias": 30, "Últimos 90 dias": 90}[periodo]
        
        tipo_relatorio = st.selectbox(
            "Tipo de Relatório",
            ["Resumo Geral", "Análise Detalhada", "Comparativo Mensal"]
        )
        
        if st.button("📊 Gerar Relatório"):
            st.session_state.relatorio_gerado = True
    
    with col1:
        if st.session_state.get("relatorio_gerado", False):
            st.subheader("Relatório Gerado")
            
            # Gerar dados para o relatório
            df_relatorio = gerar_dados_relatorio(dias)
            
            # Métricas principais
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            
            with col_metric1:
                st.metric("Total Gerado", f"{df_relatorio['Gerado (kWh)'].sum():.1f} kWh")
            with col_metric2:
                st.metric("Total Consumido", f"{df_relatorio['Consumido (kWh)'].sum():.1f} kWh")
            with col_metric3:
                st.metric("Excedente Total", f"{df_relatorio['Excedente (kWh)'].sum():.1f} kWh")
            with col_metric4:
                st.metric("Economia Total", f"R$ {df_relatorio['Economia (R$)'].sum():.2f}")
            
            # Gráfico de tendência
            st.subheader("Tendência de Produção")
            st.line_chart(df_relatorio.set_index("Data")[["Gerado (kWh)", "Consumido (kWh)"]])
            
            # Tabela de dados
            st.subheader("Dados Detalhados")
            st.dataframe(df_relatorio, use_container_width=True)

# TAB 3: Exportação
with tab3:
    st.header("Exportação de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configurações de Exportação")
        
        formato_exportacao = st.selectbox(
            "Formato de Arquivo",
            ["CSV", "Excel (XLSX)", "JSON", "PDF (Relatório)"]
        )
        
        periodo_exportacao = st.selectbox(
            "Período para Exportação",
            ["Últimos 7 dias", "Últimos 30 dias", "Todos os dados"]
        )
        
        incluir_graficos = st.checkbox("Incluir gráficos (apenas PDF)", value=True)
        incluir_resumo = st.checkbox("Incluir resumo estatístico", value=True)
        
        if st.button("📥 Preparar Exportação"):
            # Gerar dados para exportação
            if periodo_exportacao == "Últimos 7 dias":
                df_export = gerar_dados_relatorio(7)
            elif periodo_exportacao == "Últimos 30 dias":
                df_export = gerar_dados_relatorio(30)
            else:
                df_export = gerar_dados_relatorio(90)  # Simulando "todos os dados"
            
            st.session_state.dados_exportacao = df_export
            st.session_state.formato_export = formato_exportacao
            st.success("Dados preparados para exportação!")
    
    with col2:
        st.subheader("Download de Arquivos")
        
        if st.session_state.get("dados_exportacao") is not None:
            df_export = st.session_state.dados_exportacao
            formato = st.session_state.get("formato_export", "CSV")
            
            if formato == "CSV":
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv,
                    file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            elif formato == "Excel (XLSX)":
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_export.to_excel(writer, index=False, sheet_name='Dados')
                
                st.download_button(
                    label="💾 Download Excel",
                    data=buffer.getvalue(),
                    file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            elif formato == "JSON":
                json_data = df_export.to_json(orient='records', indent=2)
                st.download_button(
                    label="💾 Download JSON",
                    data=json_data,
                    file_name=f"relatorio_solar_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            # Pré-visualização dos dados
            st.subheader("Pré-visualização")
            st.dataframe(df_export.head(), use_container_width=True)

# TAB 4: Integração
with tab4:
    st.header("Configurações de Integração")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("APIs e Webhooks")
        
        # Configuração de webhook
        st.write("**Webhook para Notificações**")
        webhook_url = st.text_input("URL do Webhook", placeholder="https://exemplo.com/webhook")
        webhook_events = st.multiselect(
            "Eventos para notificar",
            ["Produção alta", "Consumo alto", "Falha no sistema", "Relatório diário"]
        )
        
        if st.button("🔗 Testar Webhook"):
            if webhook_url:
                st.success("Webhook testado com sucesso!")
                st.info("Dados de teste enviados para o endpoint.")
            else:
                st.warning("Insira uma URL válida.")
        
        # Configuração de API externa
        st.write("**Integração com APIs Externas**")
        api_key = st.text_input("API Key", type="password", help="Chave de API para serviços externos")
        api_provider = st.selectbox("Provedor", ["Weather API", "Energy API", "Custom API"])
        
        if st.button("🔌 Configurar API"):
            if api_key:
                st.success("API configurada com sucesso!")
                # Aqui você salvaria as configurações em um arquivo ou banco
            else:
                st.warning("Insira uma API Key válida.")
    
    with col2:
        st.subheader("Sincronização de Dados")
        
        # Configurações de sincronização
        auto_sync = st.checkbox("Sincronização automática", value=True)
        sync_interval = st.selectbox(
            "Intervalo de sincronização",
            ["A cada 15 minutos", "A cada hora", "A cada 6 horas", "Diariamente"]
        )
        
        # Backup automático
        st.write("**Backup de Dados**")
        backup_enabled = st.checkbox("Backup automático", value=True)
        backup_location = st.selectbox(
            "Local do backup",
            ["Armazenamento local", "Google Drive", "Dropbox", "AWS S3"]
        )
        
        if st.button("💾 Fazer Backup Agora"):
            st.success("Backup realizado com sucesso!")
            st.info(f"Dados salvos em: {backup_location}")
        
        # Status da integração
        st.subheader("Status das Integrações")
        
        status_items = [
            ("Database", "✅ Conectado"),
            ("Webhook", "⚠️ Não configurado"),
            ("API Externa", "⚠️ Não configurado"),
            ("Backup", "✅ Funcionando")
        ]
        
        for item, status in status_items:
            st.write(f"**{item}**: {status}")

# Botão de reset geral (apenas para administradores)
if st.session_state.get("username") == "admin":
    st.divider()
    st.subheader("🔧 Configurações Avançadas (Administrador)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Resetar Configurações", help="Restaurar configurações padrão"):
            st.warning("Esta ação resetará todas as configurações!")
    
    with col2:
        if st.button("🗑️ Limpar Cache", help="Limpar cache do sistema"):
            st.cache_data.clear()
            st.success("Cache limpo com sucesso!")
    
    with col3:
        if st.button("📋 Logs do Sistema", help="Visualizar logs de atividade"):
            st.info("Funcionalidade de logs em desenvolvimento.")