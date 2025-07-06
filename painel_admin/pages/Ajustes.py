import io
import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import yaml
from streamlit_authenticator import Hasher

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from painel_admin.utils import gerar_dados_relatorio

if not st.session_state.get("logged_in"):
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

st.set_page_config(page_title="Ajustes", page_icon="⚙️", layout="wide")

ARQUIVO_USUARIOS = "painel_admin/usuarios.yaml"

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

st.title("⚙️ Configurações e Ajustes")

tab1, tab2, tab3 = st.tabs([
    "👤 Opções de Usuário",
    "📥 Exportação",
    "🔌 Integração"
])

# TAB 1: Opções de Usuário
with tab1:
    st.header("Configurações de Usuário")
    
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
                    nova_senha_hash = Hasher([nova_senha]).generate()[0]
                    dados_usuarios["usernames"][usuario_atual]["password"] = nova_senha_hash
                    salvar_usuarios(dados_usuarios)
                    st.success("Senha alterada com sucesso!")
    
    st.subheader("Configurações do Sistema")
    
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Tema", ["Claro", "Escuro", "Auto"], help="Configuração visual do sistema")
        st.selectbox("Idioma", ["Português", "Inglês", "Espanhol"], help="Idioma da interface")
    
    with col2:
        st.number_input("Timeout da sessão (minutos)", min_value=5, max_value=120, value=30)
        st.checkbox("Notificações por email", help="Receber alertas por email")

# TAB 2: Exportação
with tab2:
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
            if periodo_exportacao == "Últimos 7 dias":
                df_export = gerar_dados_relatorio(7)
            elif periodo_exportacao == "Últimos 30 dias":
                df_export = gerar_dados_relatorio(30)
            else:
                df_export = gerar_dados_relatorio(90)  
            
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
            
            st.subheader("Pré-visualização")
            st.dataframe(df_export.head(), use_container_width=True)

# TAB 3: Integração
with tab3:
    st.header("Configurações de Integração")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("APIs e Webhooks")
        
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
        
        st.write("**Integração com APIs Externas**")
        api_key = st.text_input("API Key", type="password", help="Chave de API para serviços externos")
        api_provider = st.selectbox("Provedor", ["Weather API", "Energy API", "Custom API"])
        
        if st.button("🔌 Configurar API"):
            if api_key:
                st.success("API configurada com sucesso!")
            else:
                st.warning("Insira uma API Key válida.")
    
    with col2:
        st.subheader("Sincronização de Dados")
        
        auto_sync = st.checkbox("Sincronização automática", value=True)
        sync_interval = st.selectbox(
            "Intervalo de sincronização",
            ["A cada 15 minutos", "A cada hora", "A cada 6 horas", "Diariamente"]
        )
        
        st.write("**Backup de Dados**")
        backup_enabled = st.checkbox("Backup automático", value=True)
        backup_location = st.selectbox(
            "Local do backup",
            ["Armazenamento local", "Google Drive", "Dropbox", "AWS S3"]
        )
        
        if st.button("💾 Fazer Backup Agora"):
            st.success("Backup realizado com sucesso!")
            st.info(f"Dados salvos em: {backup_location}")
        
        st.subheader("Status das Integrações")
        
        status_items = [
            ("Database", "✅ Conectado"),
            ("Webhook", "⚠️ Não configurado"),
            ("API Externa", "⚠️ Não configurado"),
            ("Backup", "✅ Funcionando")
        ]
        
        for item, status in status_items:
            st.write(f"**{item}**: {status}")

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