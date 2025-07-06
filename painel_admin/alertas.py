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
        alerta = {
            'tipo': tipo,
            'mensagem': mensagem,
            'horario': horario or datetime.now().strftime('%H:%M'),
            'valor': valor,
            'timestamp': datetime.now()
        }
        self.alertas.append(alerta)
    
    def analisar_excedente(self, dados: pd.DataFrame) -> Dict[str, Any]:
        analise = {
            'excedente_total': dados['Excedente (kWh)'].sum(),
            'horas_deficit': len(dados[dados['Excedente (kWh)'] < 0]),
            'horas_sem_excedente': len(dados[dados['Excedente (kWh)'] <= 0]),
            'percentual_deficit': (len(dados[dados['Excedente (kWh)'] < 0]) / len(dados)) * 100,
            'menor_excedente': dados['Excedente (kWh)'].min(),
            'maior_excedente': dados['Excedente (kWh)'].max(),
            'media_excedente': dados['Excedente (kWh)'].mean()
        }
        
        self._gerar_alertas_excedente(dados, analise)
        
        return analise
    
    def _gerar_alertas_excedente(self, dados: pd.DataFrame, analise: Dict[str, Any]):
        self.alertas.clear() 
        
        if analise['excedente_total'] < self.configuracoes['deficit_critico']:
            self.adicionar_alerta(
                'critico',
                f"Sistema em déficit energético crítico! Déficit total: {abs(analise['excedente_total']):.2f} kWh",
                valor=analise['excedente_total']
            )
        elif analise['excedente_total'] < 0:
            self.adicionar_alerta(
                'moderado',
                f"Sistema em déficit energético. Déficit total: {abs(analise['excedente_total']):.2f} kWh",
                valor=analise['excedente_total']
            )
        elif analise['excedente_total'] == 0:
            self.adicionar_alerta(
                'atencao',
                "Sistema em equilíbrio energético - sem excedente para armazenamento",
                valor=analise['excedente_total']
            )
        
        if analise['percentual_deficit'] > self.configuracoes['percentual_critico']:
            self.adicionar_alerta(
                'critico',
                f"{analise['percentual_deficit']:.1f}% do dia com déficit energético",
                valor=analise['percentual_deficit']
            )
        
        for index, row in dados.iterrows():
            hora = row['Hora'].strftime('%H:%M')
            excedente = row['Excedente (kWh)']
            
            if excedente < self.configuracoes['deficit_critico']:
                self.adicionar_alerta(
                    'critico',
                    f"Déficit crítico às {hora}: {excedente:.2f} kWh",
                    horario=hora,
                    valor=excedente
                )
            elif excedente < 0:
                self.adicionar_alerta(
                    'moderado',
                    f"Déficit moderado às {hora}: {excedente:.2f} kWh",
                    horario=hora,
                    valor=excedente
                )
    
    def exibir_alertas(self):
        if not self.alertas:
            st.success("✅ **SISTEMA OPERANDO NORMALMENTE**: Sem alertas no momento")
            return
        
        st.subheader("🚨 Sistema de Alertas")
        
        alertas_criticos = [a for a in self.alertas if a['tipo'] == 'critico']
        alertas_moderados = [a for a in self.alertas if a['tipo'] == 'moderado']
        alertas_atencao = [a for a in self.alertas if a['tipo'] == 'atencao']
        
        if alertas_criticos:
            st.error("🔴 **ALERTAS CRÍTICOS**")
            for alerta in alertas_criticos:
                st.error(f"⚠️ {alerta['mensagem']}")
        
        if alertas_moderados:
            st.warning("🟡 **ALERTAS MODERADOS**")
            for alerta in alertas_moderados:
                st.warning(f"⚠️ {alerta['mensagem']}")
        
        if alertas_atencao:
            st.info("🟠 **ALERTAS DE ATENÇÃO**")
            for alerta in alertas_atencao:
                st.info(f"ℹ️ {alerta['mensagem']}")
    
    def gerar_recomendacoes(self, analise: Dict[str, Any]):
        st.subheader("💡 Recomendações")
        
        alertas_criticos = [a for a in self.alertas if a['tipo'] == 'critico']
        alertas_moderados = [a for a in self.alertas if a['tipo'] == 'moderado']
        
        if alertas_criticos:
            st.error("🚨 **AÇÕES URGENTES NECESSÁRIAS:**")
            st.write("- 🔧 Verificar imediatamente o funcionamento dos painéis solares")
            st.write("- ⚡ Reduzir o consumo de energia não essencial")
            st.write("- 📞 Contactar técnico especializado para manutenção")
            st.write("- 🔋 Considerar uso de energia da rede elétrica como backup")
            
        elif alertas_moderados:
            st.warning("⚠️ **RECOMENDAÇÕES PARA OTIMIZAÇÃO:**")
            st.write("- 📊 Redistribuir o consumo para horários de maior produção")
            st.write("- 🔋 Implementar sistema de armazenamento (baterias)")
            st.write("- 🧹 Realizar limpeza e manutenção preventiva dos painéis")
            st.write("- 📈 Monitorar tendências de produção vs consumo")
            
        elif analise['horas_sem_excedente'] > 0:
            st.info("💡 **SUGESTÕES DE MELHORIA:**")
            st.write("- 📋 Analisar padrões de consumo durante o dia")
            st.write("- 🌤️ Verificar condições climáticas que podem afetar a produção")
            st.write("- 🔄 Otimizar horários de uso de equipamentos de alto consumo")
            st.write("- 📊 Considerar expansão do sistema solar se necessário")
            
        else:
            st.success("🎯 **SISTEMA OTIMIZADO!**")
            st.write("✅ Continue monitorando para manter a eficiência")
            st.write("📊 Registre os dados para análise histórica")
            st.write("🔍 Monitore mudanças sazonais na produção")
    
    def exportar_alertas(self) -> pd.DataFrame:
        if not self.alertas:
            return pd.DataFrame()
        
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