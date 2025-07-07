import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
import json
import os
import logging

def carregar_configuracoes_email() -> Dict[str, Any]:
    config_file = "painel_admin/configuracoes.json"
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("email_smtp", {})
    return {}

def testar_configuracao_email(config: Dict[str, Any]) -> bool:
    try:
        servidor = config.get("servidor", "")
        porta = config.get("porta", 587)
        usuario = config.get("usuario", "")
        senha = config.get("senha", "")
        ssl = config.get("ssl", True)
        
        if not all([servidor, porta, usuario, senha]):
            return False
        
        if ssl:
            smtp_server = smtplib.SMTP(servidor, porta)
            smtp_server.starttls()
        else:
            smtp_server = smtplib.SMTP(servidor, porta)
        
        smtp_server.login(usuario, senha)
        smtp_server.quit()
        return True
        
    except Exception as e:
        logging.error(f"Erro ao testar configuração de email: {e}")
        return False

def enviar_email(
    destinatario: str,
    assunto: str,
    corpo: str,
    corpo_html: Optional[str] = None,
    anexos: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    try:
        email_config = config or carregar_configuracoes_email()
        
        servidor = email_config.get("servidor", "")
        porta = email_config.get("porta", 587)
        usuario = email_config.get("usuario", "")
        senha = email_config.get("senha", "")
        ssl = email_config.get("ssl", True)
        
        if not all([servidor, porta, usuario, senha]):
            logging.error("Configurações de email incompletas")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['From'] = usuario
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        if corpo:
            part1 = MIMEText(corpo, 'plain', 'utf-8')
            msg.attach(part1)
        
        if corpo_html:
            part2 = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(part2)
        
        if anexos:
            for arquivo in anexos:
                if os.path.exists(arquivo):
                    with open(arquivo, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(arquivo)}'
                    )
                    
                    msg.attach(part)
        
        if ssl:
            smtp_server = smtplib.SMTP(servidor, porta)
            smtp_server.starttls()
        else:
            smtp_server = smtplib.SMTP(servidor, porta)
        
        smtp_server.login(usuario, senha)
        
        text = msg.as_string()
        smtp_server.sendmail(usuario, destinatario, text)
        smtp_server.quit()
        
        logging.info(f"Email enviado com sucesso para {destinatario}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao enviar email: {e}")
        return False

def enviar_notificacao_alerta(
    tipo_alerta: str,
    mensagem: str,
    nivel: str = "info",
    destinatario: Optional[str] = None
) -> bool:
    try:
        config_geral = {}
        config_file = "painel_admin/configuracoes.json"
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config_geral = json.load(f)
        
        if not config_geral.get("notificacoes_email", False):
            return False
        
        if not destinatario:
            from streamlit import session_state
            if "username" in session_state:
                import yaml
                usuarios_file = "painel_admin/usuarios.yaml"
                if os.path.exists(usuarios_file):
                    with open(usuarios_file, "r") as f:
                        usuarios = yaml.safe_load(f) or {}
                    
                    username = session_state.get("username")
                    if username in usuarios.get("usernames", {}):
                        destinatario = usuarios["usernames"][username].get("email", "")
        
        if not destinatario:
            logging.warning("Nenhum destinatário definido para notificação de alerta")
            return False
        
        emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "🚨"
        }
        
        cores = {
            "info": "#17a2b8",
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        
        emoji = emojis.get(nivel, "ℹ️")
        cor = cores.get(nivel, "#17a2b8")
        
        assunto = f"{emoji} Sistema Solar - {tipo_alerta}"
        
        from datetime import datetime
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        corpo_texto = f"""
Sistema de Monitoramento Solar - Alerta

Tipo: {tipo_alerta}
Nível: {nivel.upper()}
Mensagem: {mensagem}

Data/Hora: {data_hora}

---
Este é um alerta automático do Sistema de Monitoramento Solar.
        """
        
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: {cor}; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f8f9fa; padding: 20px; border-left: 4px solid {cor}; }}
                .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; }}
                .alert-box {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{emoji} Sistema de Monitoramento Solar</h1>
                    <h2>Alerta: {tipo_alerta}</h2>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <h3>Detalhes do Alerta</h3>
                        <p><strong>Tipo:</strong> {tipo_alerta}</p>
                        <p><strong>Nível:</strong> {nivel.upper()}</p>
                        <p><strong>Mensagem:</strong> {mensagem}</p>
                                                 <p><strong>Data/Hora:</strong> {data_hora}</p>
                    </div>
                </div>
                <div class="footer">
                    <p>Este é um alerta automático do Sistema de Monitoramento Solar.</p>
                    <p>Para mais informações, acesse o painel de administração.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return enviar_email(
            destinatario=destinatario,
            assunto=assunto,
            corpo=corpo_texto,
            corpo_html=corpo_html
        )
        
    except Exception as e:
        logging.error(f"Erro ao enviar notificação de alerta: {e}")
        return False

def enviar_email_teste(destinatario: str, config: Optional[Dict[str, Any]] = None) -> bool:
    assunto = "🔧 Teste de Configuração - Sistema Solar"
    
    corpo_texto = """
Sistema de Monitoramento Solar - Teste de Email

Este é um email de teste para verificar se as configurações de email estão funcionando corretamente.

Se você recebeu este email, significa que:
✅ As configurações SMTP estão corretas
✅ O servidor de email está acessível
✅ As credenciais de autenticação estão válidas

Sistema funcionando normalmente!

---
Sistema de Monitoramento Solar
    """
    
    corpo_html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; }
            .header { background-color: #28a745; color: white; padding: 20px; text-align: center; }
            .content { background-color: #f8f9fa; padding: 20px; }
            .success { background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; }
            .footer { background-color: #e9ecef; padding: 15px; text-align: center; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 Sistema de Monitoramento Solar</h1>
                <h2>Teste de Configuração</h2>
            </div>
            <div class="content">
                <div class="success">
                    <h3>✅ Teste Realizado com Sucesso!</h3>
                    <p>Este é um email de teste para verificar se as configurações de email estão funcionando corretamente.</p>
                </div>
                <h3>Verificações Realizadas:</h3>
                <ul>
                    <li>✅ Configurações SMTP estão corretas</li>
                    <li>✅ Servidor de email está acessível</li>
                    <li>✅ Credenciais de autenticação estão válidas</li>
                </ul>
                <p><strong>Sistema funcionando normalmente!</strong></p>
            </div>
            <div class="footer">
                <p>Sistema de Monitoramento Solar - Teste Automático</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return enviar_email(
        destinatario=destinatario,
        assunto=assunto,
        corpo=corpo_texto,
        corpo_html=corpo_html,
        config=config
    ) 