import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import time
import random
from typing import Dict, List, Any
from dotenv import load_dotenv

class EmailService:
    """Serviço para envio de emails com avaliações"""
    
    def __init__(self):
        self.config = self._carregar_config()
    
    def _carregar_config(self) -> Dict[str, Any]:
        """Carrega configuração de email"""
        # Carregar variáveis de ambiente do arquivo .env (com override=True para garantir)
        load_dotenv('config/email.env', override=True)
        
        # Tentar carregar do arquivo JSON primeiro (para compatibilidade)
        try:
            with open('config/email_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Usar variáveis de ambiente (com strip para remover espaços)
            password = os.getenv("SENDER_PASSWORD", "").strip()
            email = os.getenv("SENDER_EMAIL", "").strip()
            
            print(f"DEBUG - Email carregado: {email}")
            print(f"DEBUG - Password carregado: {'*' * len(password) if password else 'VAZIO'}")
            
            config = {
                "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "sender_email": email,
                "sender_password": password,
                "use_tls": os.getenv("USE_TLS", "true").lower() == "true",
                "app_name": os.getenv("APP_NAME", "Sistema de Avaliação de Pares")
            }
            
            # Garantir que não há valores vazios
            if not config["sender_password"]:
                raise ValueError("SENDER_PASSWORD não foi carregado corretamente do email.env")
            if not config["sender_email"]:
                raise ValueError("SENDER_EMAIL não foi carregado corretamente do email.env")
            
            return config
    
    def enviar_avaliacoes(self, destinatario: str, nome_usuario: str, avaliacoes_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Envia email com avaliações do usuário
        
        Args:
            destinatario: Email do destinatário
            nome_usuario: Nome do usuário
            avaliacoes_data: Dados das avaliações
            
        Returns:
            Tupla com (sucesso, mensagem)
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = destinatario
            msg['Subject'] = f"📊 Suas Avaliações - {avaliacoes_data.get('sprint', 'Sprint Atual')}"
            
            # Corpo do email
            body = self._criar_corpo_email(nome_usuario, avaliacoes_data)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Enviar email
            self._enviar_email(msg)
            return True, "Email enviado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    def _criar_corpo_email(self, nome_usuario: str, avaliacoes_data: Dict[str, Any]) -> str:
        """
        Cria o corpo HTML do email
        
        Args:
            nome_usuario: Nome do usuário
            avaliacoes_data: Dados das avaliações
            
        Returns:
            String HTML do corpo do email
        """
        sprint = avaliacoes_data.get('sprint', 'Sprint Atual')
        grupo = avaliacoes_data.get('grupo', 'Grupo')
        
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background-color: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background-color: white; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
                    overflow: hidden; 
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px; 
                    text-align: center; 
                }}
                .header h1 {{ 
                    margin: 0; 
                    font-size: 28px; 
                    font-weight: 300; 
                }}
                .header p {{ 
                    margin: 10px 0 0 0; 
                    font-size: 16px; 
                    opacity: 0.9; 
                }}
                .content {{ 
                    padding: 30px; 
                }}
                .info-box {{ 
                    background-color: #e3f2fd; 
                    border-left: 4px solid #2196f3; 
                    padding: 20px; 
                    margin: 20px 0; 
                    border-radius: 5px; 
                }}
                .avaliacao {{ 
                    margin: 25px 0; 
                    padding: 20px; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 10px; 
                    background-color: #fafafa; 
                }}
                .aluno-nome {{ 
                    font-size: 20px; 
                    font-weight: bold; 
                    color: #1976d2; 
                    margin-bottom: 15px; 
                    padding-bottom: 10px; 
                    border-bottom: 2px solid #e3f2fd; 
                }}
                .eixo-container {{ 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    margin: 10px 0; 
                    padding: 10px; 
                    background-color: white; 
                    border-radius: 5px; 
                }}
                .eixo-info {{ 
                    flex: 1; 
                }}
                .eixo-nome {{ 
                    font-weight: bold; 
                    color: #424242; 
                    margin-bottom: 5px; 
                }}
                .nota {{ 
                    font-size: 18px; 
                    font-weight: bold; 
                    color: #2e7d32; 
                    background-color: #e8f5e8; 
                    padding: 5px 12px; 
                    border-radius: 20px; 
                    min-width: 40px; 
                    text-align: center; 
                }}
                .feedback {{ 
                    margin-top: 15px; 
                    padding: 15px; 
                    background-color: #fff3e0; 
                    border-left: 4px solid #ff9800; 
                    border-radius: 5px; 
                }}
                .feedback-title {{ 
                    font-weight: bold; 
                    color: #e65100; 
                    margin-bottom: 8px; 
                }}
                .footer {{ 
                    background-color: #f5f5f5; 
                    padding: 20px; 
                    text-align: center; 
                    color: #666; 
                    font-size: 14px; 
                }}
                .footer ul {{ 
                    list-style: none; 
                    padding: 0; 
                    margin: 15px 0; 
                }}
                .footer li {{ 
                    margin: 8px 0; 
                    padding: 5px 0; 
                }}
                .footer li:before {{ 
                    content: "• "; 
                    color: #1976d2; 
                    font-weight: bold; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Suas Avaliações</h1>
                    <p>{sprint} • Grupo {grupo}</p>
                </div>
                
                <div class="content">
                    <div class="info-box">
                        <h3>👋 Olá, {nome_usuario}!</h3>
                        <p>Aqui estão as avaliações que você realizou para o grupo <strong>{grupo}</strong> na {sprint}.</p>
                        <p>Total de avaliações: <strong>{len(avaliacoes_data.get('avaliacoes', []))}</strong></p>
                    </div>
        """
        
        # Adicionar cada avaliação
        avaliacoes = avaliacoes_data.get('avaliacoes', [])
        if avaliacoes:
            for avaliacao in avaliacoes:
                html += f"""
                <div class="avaliacao">
                    <div class="aluno-nome">👤 {avaliacao.get('aluno_avaliado', 'Aluno')}</div>
                    
                    <div class="eixo-container">
                        <div class="eixo-info">
                            <div class="eixo-nome">Eixo 1: Entregas reais</div>
                        </div>
                        <div class="nota">{avaliacao.get('nota_eixo1', 0)}</div>
                    </div>
                    
                    <div class="eixo-container">
                        <div class="eixo-info">
                            <div class="eixo-nome">Eixo 2: Valor Percebido</div>
                        </div>
                        <div class="nota">{avaliacao.get('nota_eixo2', 0)}</div>
                    </div>
                    
                    <div class="eixo-container">
                        <div class="eixo-info">
                            <div class="eixo-nome">Eixo 3: Caixa de Ferramentas</div>
                        </div>
                        <div class="nota">{avaliacao.get('nota_eixo3', 0)}</div>
                    </div>
                    
                    <div class="feedback">
                        <div class="feedback-title">📝 Feedbacks:</div>
                        <p><strong>Entregas reais:</strong> {avaliacao.get('feedback_eixo1', 'N/A')}</p>
                        <p><strong>Valor Percebido:</strong> {avaliacao.get('feedback_eixo2', 'N/A')}</p>
                        <p><strong>Caixa de Ferramentas:</strong> {avaliacao.get('feedback_eixo3', 'N/A')}</p>
                    </div>
                </div>
                """
        else:
            html += """
            <div class="avaliacao">
                <p>Nenhuma avaliação encontrada para esta sprint.</p>
            </div>
            """
        
        html += """
                </div>
                
                <div class="footer">
                    <h4>📋 Informações Importantes:</h4>
                    <ul>
                        <li>Estas são as avaliações que você realizou na sprint atual</li>
                        <li>Guarde este email para referência futura</li>
                        <li>As avaliações são confidenciais e pessoais</li>
                        <li>Em caso de dúvidas, entre em contato com o Professor Orientador</li>
                    </ul>
                    <p style="margin-top: 20px; font-size: 12px; color: #999;">
                        Sistema de Avaliação de Pares • Inteli
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _enviar_email(self, msg: MIMEMultipart, max_retries: int = 3) -> None:
        """
        Envia o email via SMTP com sistema de retry
        
        Args:
            msg: Mensagem de email preparada
            max_retries: Número máximo de tentativas
        """
        last_exception = None
        server = None
        
        for attempt in range(max_retries):
            try:
                # Aguardar com delay progressivo (0.5s, 1s, 2s)
                delay = 0.5 + (attempt * 0.5) + random.uniform(0, 0.5)
                print(f"📧 Tentativa {attempt + 1}/{max_retries} - Aguardando {delay:.1f}s...")
                time.sleep(delay)
                
                # Criar conexão SMTP (EXATAMENTE como no teste que funcionou)
                print(f"🔄 Conectando a {self.config['smtp_server']}:{self.config['smtp_port']}...")
                server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
                server.set_debuglevel(0)
                
                if self.config['use_tls']:
                    server.starttls()
                
                # Login com timeout
                server.login(self.config['sender_email'], self.config['sender_password'])
                
                # Enviar mensagem
                server.send_message(msg)
                server.quit()
                
                print(f"✅ Email enviado com sucesso na tentativa {attempt + 1}")
                return  # Sucesso, sair da função
                
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ Erro de autenticação (tentativa {attempt + 1}): {str(e)}")
                last_exception = e
                if "temporary system problem" in str(e).lower():
                    print("🔄 Problema temporário detectado, tentando novamente...")
                    # Fechar servidor antes de continuar
                    if server:
                        try:
                            server.quit()
                        except:
                            pass
                    continue
                else:
                    # Fechar servidor antes de levantar exceção
                    if server:
                        try:
                            server.quit()
                        except:
                            pass
                    raise e  # Erro de autenticação permanente
                    
            except smtplib.SMTPRecipientsRefused as e:
                print(f"❌ Destinatário recusado (tentativa {attempt + 1}): {str(e)}")
                # Fechar servidor antes de levantar exceção
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                raise e  # Não tentar novamente para este erro
                
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, ConnectionError, TimeoutError) as e:
                print(f"❌ Erro de conexão (tentativa {attempt + 1}): {str(e)}")
                last_exception = e
                # Fechar servidor antes de continuar
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                server = None  # Resetar para próxima tentativa
                continue
                
            except smtplib.SMTPException as e:
                print(f"❌ Erro SMTP (tentativa {attempt + 1}): {str(e)}")
                last_exception = e
                if "temporary" in str(e).lower() or "try again" in str(e).lower():
                    print("🔄 Erro temporário detectado, tentando novamente...")
                    # Fechar servidor antes de continuar
                    if server:
                        try:
                            server.quit()
                        except:
                            pass
                    server = None
                    continue
                else:
                    # Fechar servidor antes de levantar exceção
                    if server:
                        try:
                            server.quit()
                        except:
                            pass
                    raise e
                    
            except Exception as e:
                print(f"❌ Erro inesperado (tentativa {attempt + 1}): {str(e)}")
                print(f"Tipo do erro: {type(e).__name__}")
                last_exception = e
                # Fechar servidor antes de continuar
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                server = None  # Resetar para próxima tentativa
                continue
                
            finally:
                # Garantir que servidor seja fechado
                if server:
                    try:
                        server.quit()
                    except:
                        pass
        
        # Se chegou aqui, todas as tentativas falharam
        raise last_exception or Exception("Falha ao enviar email após todas as tentativas")
    
    def enviar_confirmacao_cadastro(self, destinatario: str, nome_usuario: str, turma: str, grupo: str) -> tuple[bool, str]:
        """
        Envia email de confirmação de cadastro
        
        Args:
            destinatario: Email do destinatário
            nome_usuario: Nome do usuário
            turma: Turma do usuário
            grupo: Grupo do usuário
            
        Returns:
            Tupla com (sucesso, mensagem)
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = destinatario
            msg['Subject'] = "🎉 Cadastro Realizado com Sucesso - Sistema de Avaliação de Pares"
            
            # Corpo do email
            body = self._criar_corpo_email_cadastro(nome_usuario, turma, grupo)
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Enviar email
            self._enviar_email(msg)
            return True, "Email de confirmação enviado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao enviar email de confirmação: {str(e)}"
    
    def _criar_corpo_email_cadastro(self, nome_usuario: str, turma: str, grupo: str) -> str:
        """
        Cria o corpo HTML do email de confirmação de cadastro
        
        Args:
            nome_usuario: Nome do usuário
            turma: Turma do usuário
            grupo: Grupo do usuário
            
        Returns:
            String HTML do corpo do email
        """
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background-color: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background-color: white; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
                    overflow: hidden; 
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px; 
                    text-align: center; 
                }}
                .header h1 {{ 
                    margin: 0; 
                    font-size: 28px; 
                    font-weight: 300; 
                }}
                .content {{ 
                    padding: 30px; 
                }}
                .info-box {{ 
                    background-color: #e8f5e8; 
                    border-left: 4px solid #4caf50; 
                    padding: 20px; 
                    margin: 20px 0; 
                    border-radius: 5px; 
                }}
                .info-item {{ 
                    margin: 10px 0; 
                    padding: 10px; 
                    background-color: white; 
                    border-radius: 5px; 
                    border: 1px solid #e0e0e0; 
                }}
                .info-label {{ 
                    font-weight: bold; 
                    color: #1976d2; 
                }}
                .footer {{ 
                    background-color: #f5f5f5; 
                    padding: 20px; 
                    text-align: center; 
                    color: #666; 
                    font-size: 14px; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Cadastro Realizado!</h1>
                    <p>Sistema de Avaliação de Pares</p>
                </div>
                
                <div class="content">
                    <div class="info-box">
                        <h3>👋 Olá, {nome_usuario}!</h3>
                        <p>Seu cadastro foi realizado com sucesso no Sistema de Avaliação de Pares.</p>
                    </div>
                    
                    <h3>📋 Suas Informações:</h3>
                    
                    <div class="info-item">
                        <span class="info-label">👤 Nome:</span> {nome_usuario}
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">🏫 Turma:</span> {turma}
                    </div>
                    
                    <div class="info-item">
                        <span class="info-label">👥 Grupo:</span> {grupo}
                    </div>
                    
                    <div class="info-box">
                        <h4>🚀 Próximos Passos:</h4>
                        <ul>
                            <li>Faça login no sistema usando seu email institucional</li>
                            <li>Acesse as avaliações da sua turma e grupo</li>
                            <li>Participe das avaliações de pares nas sprints disponíveis</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>Sistema de Avaliação de Pares</strong></p>
                    <p>Inteli - Instituto de Tecnologia e Liderança</p>
                    <p style="margin-top: 15px; font-size: 12px; color: #999;">
                        Este é um email automático. Não responda a esta mensagem.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

    def testar_conexao(self) -> tuple[bool, str]:
        """
        Testa a conexão com o servidor SMTP com retry
        
        Returns:
            Tupla com (sucesso, mensagem)
        """
        try:
            # Usar o mesmo método de envio, mas sem mensagem
            print("🔍 Testando conexão SMTP...")
            
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.set_debuglevel(0)
            server.timeout = 30
            
            if self.config['use_tls']:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                server.starttls(context=context)
            
            server.login(self.config['sender_email'], self.config['sender_password'])
            server.quit()
            
            return True, "✅ Conexão SMTP testada com sucesso!"
            
        except smtplib.SMTPAuthenticationError as e:
            if "temporary system problem" in str(e).lower():
                return False, f"⚠️ Problema temporário no Gmail: {str(e)}"
            else:
                return False, f"❌ Erro de autenticação: {str(e)}"
        except Exception as e:
            return False, f"❌ Erro na conexão SMTP: {str(e)}"
