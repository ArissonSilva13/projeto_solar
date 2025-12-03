import streamlit as st
from datetime import datetime
from typing import Dict, Any
import pandas as pd

class SistemaAlertas:
    
    def __init__(self):
        self.alertas = []
        self.configuracoes = {
            'deficit_critico': -2.0, 
            'deficit_moderado': 0.0,
            'horas_criticas': 6,
            'percentual_critico': 25.0
        }
    
    def adicionar_alerta(self, tipo: str, mensagem: str, horario: str = None, valor: float = None):
        """
        Registra um novo alerta no sistema.
        """
        alerta = {
            'tipo': tipo,
            'mensagem': mensagem,
            'horario': horario or datetime.now().strftime('%H:%M'),
            'valor': valor,
            'timestamp': datetime.now()
        }
        self.alertas.append(alerta)
    
    def analisar_excedente(self, dados: pd.DataFrame) -> Dict[str, Any]:
        """
        Processa os dados do dataframe para identificar anomalias.
        """
        # Garante que a coluna Excedente existe
        if 'Excedente (kWh)' not in dados.columns:
            if 'Gerado (kWh)' in dados.columns and 'Consumido (kWh)' in dados.columns:
                dados['Excedente (kWh)'] = dados['Gerado (kWh)'] - dados['Consumido (kWh)']
            else:
                return {}

        analise = {
            'excedente_total': dados['Excedente (kWh)'].sum(),
            'horas_deficit': len(dados[dados['Excedente (kWh)'] < 0]),
            'horas_sem_excedente': len(dados[dados['Excedente (kWh)'] <= 0]),
            'percentual_deficit': (len(dados[dados['Excedente (kWh)'] < 0]) / len(dados)) * 100 if len(dados) > 0 else 0,
            'menor_excedente': dados['Excedente (kWh)'].min(),
            'maior_excedente': dados['Excedente (kWh)'].max(),
            'media_excedente': dados['Excedente (kWh)'].mean()
        }
        
        self._gerar_alertas_excedente(dados, analise)
        
        return analise
    
    def _gerar_alertas_excedente(self, dados: pd.DataFrame, analise: Dict[str, Any]):
        """
        Lógica interna para popular a lista de alertas baseada nos dados.
        """
        self.alertas.clear() 
        
        # 1. Análise do Total
        if analise['excedente_total'] < self.configuracoes['deficit_critico']:
            self.adicionar_alerta(
                'critico',
                f"Déficit Energético Crítico: O sistema consumiu {abs(analise['excedente_total']):.2f} kWh a mais do que gerou.",
                valor=analise['excedente_total']
            )
        elif analise['excedente_total'] < 0:
            self.adicionar_alerta(
                'moderado',
                f"Balanço Negativo: Déficit leve de {abs(analise['excedente_total']):.2f} kWh.",
                valor=analise['excedente_total']
            )
        elif analise['excedente_total'] == 0:
            self.adicionar_alerta(
                'atencao',
                "Equilíbrio Estático: Sem excedente para armazenamento.",
                valor=analise['excedente_total']
            )
        
        # 2. Análise de Tempo de Déficit
        if analise['percentual_deficit'] > self.configuracoes['percentual_critico']:
            self.adicionar_alerta(
                'critico',
                f"Cobertura Insuficiente: {analise['percentual_deficit']:.1f}% do tempo operando com déficit.",
                valor=analise['percentual_deficit']
            )
        
        # 3. Análise Pontual (Horária)
        for index, row in dados.iterrows():
            # Tenta pegar hora de diferentes formatos
            if 'Hora' in row:
                if isinstance(row['Hora'], str):
                    hora = row['Hora']
                else:
                    try:
                        hora = row['Hora'].strftime('%H:%M')
                    except:
                        hora = str(index)
            else:
                hora = str(index)

            excedente = row['Excedente (kWh)']
            
            if excedente < self.configuracoes['deficit_critico']:
                self.adicionar_alerta(
                    'critico',
                    f"Pico de Consumo às {hora}: Déficit de {excedente:.2f} kWh",
                    horario=hora,
                    valor=excedente
                )
    
    def exibir_alertas(self):
        """
        Renderiza o Dashboard de Saúde do Sistema (Visual Novo).
        """
        if not self.alertas:
            st.success("✅ **SISTEMA SAUDÁVEL**: Operação nominal sem alertas.")
            return
        
        # --- 1. KPIs de Saúde (Novo) ---
        stats = self.get_estatisticas()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Eventos", stats['total'])
        col2.metric("🚨 Críticos", stats['criticos'], delta="-Ação Necessária" if stats['criticos'] > 0 else "Normal", delta_color="inverse")
        col3.metric("⚠️ Moderados", stats['moderados'])
        col4.metric("ℹ️ Informativos", stats['atencao'])
        
        st.divider()
        
        # --- 2. Lista de Alertas em Cards ---
        st.subheader("📋 Log de Eventos")
        
        # Filtro rápido
        filtro = st.radio("Filtrar visualização:", ["Todos", "Apenas Críticos", "Críticos e Moderados"], horizontal=True)
        
        lista_exibicao = self.alertas
        if filtro == "Apenas Críticos":
            lista_exibicao = [a for a in self.alertas if a['tipo'] == 'critico']
        elif filtro == "Críticos e Moderados":
            lista_exibicao = [a for a in self.alertas if a['tipo'] in ['critico', 'moderado']]
            
        if not lista_exibicao:
            st.info("Nenhum alerta para este filtro.")
        
        for alerta in lista_exibicao:
            # Define estilo do card baseado no tipo
            if alerta['tipo'] == 'critico':
                icon = "🔴"
                border_color = "red"
                bg_color = "#FEF2F2" # Fundo avermelhado bem claro
            elif alerta['tipo'] == 'moderado':
                icon = "🟡"
                border_color = "orange"
                bg_color = "#FFFBEB" # Fundo amarelado
            else:
                icon = "🔵"
                border_color = "blue"
                bg_color = "#EFF6FF" # Fundo azulado
            
            # Renderiza o Card
            with st.container():
                col_icon, col_msg, col_time = st.columns([0.5, 8, 1.5])
                with col_icon:
                    st.write(f"### {icon}")
                with col_msg:
                    st.markdown(f"**{alerta['mensagem']}**")
                    if alerta['valor'] is not None:
                        st.caption(f"Valor registrado: {alerta['valor']:.2f}")
                with col_time:
                    st.caption(f"🕒 {alerta['horario']}")
                st.markdown("---") # Divisor fino entre alertas

    def gerar_recomendacoes(self, analise: Dict[str, Any]):
        """
        Renderiza o painel de recomendações inteligentes.
        """
        with st.expander("💡 Assistente de Otimização (Recomendações)", expanded=True):
            
            alertas_criticos = [a for a in self.alertas if a['tipo'] == 'critico']
            alertas_moderados = [a for a in self.alertas if a['tipo'] == 'moderado']
            
            if alertas_criticos:
                st.error("🚨 **AÇÃO IMEDIATA REQUERIDA**")
                st.markdown("""
                * **Verificação de Hardware:** Inspecione inversores e cabeamento por superaquecimento.
                * **Redução de Carga:** Desligue equipamentos não essenciais imediatamente.
                * **Backup:** Verifique se o banco de baterias (se houver) está entrando em operação.
                """)
                
            elif alertas_moderados:
                st.warning("⚠️ **SUGESTÕES DE MELHORIA**")
                st.markdown("""
                * **Shift de Carga:** Tente mover o uso de máquinas pesadas para o horário de pico solar (11h-14h).
                * **Limpeza:** Verifique se há sujeira ou sombreamento parcial nos painéis.
                """)
                
            elif analise.get('horas_sem_excedente', 0) > 0:
                st.info("ℹ️ **DICAS DE EFICIÊNCIA**")
                st.markdown("""
                * O sistema está estável, mas sem sobras. Considere expansão se pretender adicionar novos equipamentos.
                """)
            
            else:
                st.success("✨ **SISTEMA OTIMIZADO**")
                st.markdown("A operação está perfeita. Nenhum ajuste necessário no momento.")

    def exportar_alertas(self) -> pd.DataFrame:
        if not self.alertas:
            return pd.DataFrame(columns=["Tipo", "Mensagem", "Horário", "Valor"])
        return pd.DataFrame(self.alertas)
    
    def configurar_limites(self, **kwargs):
        self.configuracoes.update(kwargs)
    
    def get_estatisticas(self) -> Dict[str, int]:
        return {
            'total': len(self.alertas),
            'criticos': len([a for a in self.alertas if a['tipo'] == 'critico']),
            'moderados': len([a for a in self.alertas if a['tipo'] == 'moderado']),
            'atencao': len([a for a in self.alertas if a['tipo'] == 'atencao'])
        }