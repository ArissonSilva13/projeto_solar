import streamlit as st
from datetime import datetime, timedelta

class NotificacaoRealTime:
    
    def __init__(self):
        if 'notificacoes' not in st.session_state:
            st.session_state.notificacoes = []
        if 'ultima_verificacao' not in st.session_state:
            st.session_state.ultima_verificacao = datetime.now()
    
    def adicionar_notificacao(self, tipo: str, titulo: str, mensagem: str, urgencia: str = 'baixa'):
        notificacao = {
            'id': len(st.session_state.notificacoes) + 1,
            'tipo': tipo,
            'titulo': titulo,
            'mensagem': mensagem,
            'urgencia': urgencia,
            'timestamp': datetime.now(),
            'lida': False
        }
        st.session_state.notificacoes.append(notificacao)
    
    def marcar_como_lida(self, notificacao_id: int):
        for notif in st.session_state.notificacoes:
            if notif['id'] == notificacao_id:
                notif['lida'] = True
                break
    
    def obter_notificacoes_nao_lidas(self):
        return [n for n in st.session_state.notificacoes if not n['lida']]
    
    def limpar_notificacoes_antigas(self, horas: int = 24):
        tempo_limite = datetime.now() - timedelta(hours=horas)
        st.session_state.notificacoes = [
            n for n in st.session_state.notificacoes 
            if n['timestamp'] > tempo_limite
        ]
    
    def exibir_toast(self, notificacao):
        if notificacao['urgencia'] == 'alta':
            st.error(f"🚨 **{notificacao['titulo']}**: {notificacao['mensagem']}")
        elif notificacao['urgencia'] == 'media':
            st.warning(f"⚠️ **{notificacao['titulo']}**: {notificacao['mensagem']}")
        else:
            st.info(f"ℹ️ **{notificacao['titulo']}**: {notificacao['mensagem']}")
    
    def exibir_painel_notificacoes(self):
        nao_lidas = self.obter_notificacoes_nao_lidas()
        
        if nao_lidas:
            st.sidebar.subheader(f"🔔 Notificações ({len(nao_lidas)})")
            
            for notif in nao_lidas[-5:]:  
                with st.sidebar.expander(f"{notif['titulo']} - {notif['timestamp'].strftime('%H:%M')}"):
                    st.write(notif['mensagem'])
                    if st.button(f"Marcar como lida", key=f"read_{notif['id']}"):
                        self.marcar_como_lida(notif['id'])
                        st.rerun()
        else:
            st.sidebar.info("🔔 Nenhuma notificação nova")
    
    def verificar_alertas_excedente(self, dados):
        excedente_total = dados['Excedente (kWh)'].sum()
        horas_deficit = len(dados[dados['Excedente (kWh)'] < 0])
        
        if excedente_total < -5:
            self.adicionar_notificacao(
                'deficit_critico',
                'Déficit Energético Crítico',
                f'Sistema com déficit de {abs(excedente_total):.2f} kWh',
                'alta'
            )
        
        if horas_deficit > 12:
            self.adicionar_notificacao(
                'horas_deficit',
                'Muitas Horas em Déficit',
                f'{horas_deficit} horas do dia sem excedente',
                'media'
            )
        
        if excedente_total <= 0:
            self.adicionar_notificacao(
                'sem_excedente',
                'Sistema Sem Excedente',
                'Sistema operando sem excedente de energia',
                'baixa'
            )
    
    def auto_refresh_alertas(self):
        if st.sidebar.button("🔄 Atualizar Alertas"):
            st.session_state.ultima_verificacao = datetime.now()
            st.rerun()
        
        st.sidebar.caption(f"Última verificação: {st.session_state.ultima_verificacao.strftime('%H:%M:%S')}") 