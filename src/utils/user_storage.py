import json
import os
import bcrypt
from pathlib import Path
from src.utils.audit_logger import AuditLogger

class UserStorage:
    """Classe para gerenciar armazenamento local de usuários"""
    
    def __init__(self):
        self.users_dir = Path("data/usuarios")
        self.users_dir.mkdir(exist_ok=True)
        self.users_file = self.users_dir / "usuarios.json"
        self.audit_logger = AuditLogger()
        self._load_users()
    
    def _load_users(self):
        """Carrega usuários do arquivo JSON"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users_raw = json.load(f)
                    # Normalizar todas as chaves de email para minúsculas
                    # Garantir que 'data' é um dicionário
                    self.users = {
                        email.lower(): data 
                        for email, data in users_raw.items() 
                        if isinstance(data, dict)
                    }
            except (json.JSONDecodeError, FileNotFoundError):
                self.users = {}
        else:
            self.users = {}
    
    def _save_users(self):
        """Salva usuários no arquivo JSON"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2, ensure_ascii=False)
    
    def user_exists(self, email):
        """Verifica se um usuário existe"""
        email_normalizado = email.lower()
        return email_normalizado in self.users
    
    def is_pre_registered(self, email):
        """Verifica se o usuário está pré-cadastrado (sem senha)"""
        email_normalizado = email.lower()
        if email_normalizado in self.users:
            return not self.users[email_normalizado].get("passwd")  # Novo campo: passwd
        return False
    
    def create_user(self, email, username, password, turma, grupo):
        """Cria um novo usuário ou atualiza um pré-cadastrado"""
        email_normalizado = email.lower()
        if self.user_exists(email_normalizado):
            # Verificar se é um usuário pré-cadastrado
            if self.is_pre_registered(email_normalizado):
                # Atualizar usuário pré-cadastrado com senha
                return self._update_pre_registered_user(email_normalizado, password)
            else:
                return False, "Usuário já existe"
        
        # Criar novo usuário
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.users[email_normalizado] = {
            "name": username,  # Novo campo: name
            "passwd": password_hash,  # Novo campo: passwd
            "turma": turma,
            "id": None  # Será definido se for aluno
        }
        
        self._save_users()
        
        # Registrar na auditoria
        self.audit_logger.log_cadastro(email, username, turma, grupo)
        
        # Enviar email de confirmação de cadastro
        try:
            from src.utils.email_service import EmailService
            email_service = EmailService()
            success_email, message_email = email_service.enviar_confirmacao_cadastro(email, username, turma, grupo)
            if not success_email:
                print(f"Aviso: Email de confirmação não foi enviado: {message_email}")
        except Exception as e:
            print(f"Aviso: Erro ao enviar email de confirmação: {str(e)}")
        
        return True, "Usuário criado com sucesso"
    
    def _update_pre_registered_user(self, email, password):
        """Atualiza usuário pré-cadastrado com senha"""
        if not self.is_pre_registered(email):
            return False, "Usuário não está pré-cadastrado"
        
        # Criptografar senha
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Atualizar usuário
        self.users[email]["passwd"] = password_hash  # Novo campo: passwd
        
        self._save_users()
        
        # Registrar na auditoria
        self.audit_logger.log_cadastro(
            email, 
            self.users[email]["name"],  # Novo campo: name
            self.users[email]["turma"], 
            "Grupo"  # Placeholder para grupo
        )
        
        # Enviar email de confirmação de ativação de conta
        try:
            from src.utils.email_service import EmailService
            email_service = EmailService()
            success_email, message_email = email_service.enviar_confirmacao_cadastro(
                email, 
                self.users[email]["name"], 
                self.users[email]["turma"], 
                "Grupo"
            )
            if not success_email:
                print(f"Aviso: Email de confirmação não foi enviado: {message_email}")
        except Exception as e:
            print(f"Aviso: Erro ao enviar email de confirmação: {str(e)}")
        
        return True, "Usuário pré-cadastrado ativado com sucesso"
    
    def update_password(self, email, new_password):
        """Atualiza a senha de um usuário"""
        email_normalizado = email.lower()
        if not self.user_exists(email_normalizado):
            return False, "Usuário não encontrado"
        
        user = self.users[email_normalizado]
        
        # Verificar se o usuário já tem uma senha cadastrada
        if not user.get("passwd"):
            return False, "Usuário sem senha cadastrada. Faça seu cadastro primeiro."
        
        # Criptografar nova senha
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.users[email_normalizado]["passwd"] = password_hash  # Novo campo: passwd
        self._save_users()
        
        # Registrar na auditoria
        self.audit_logger.log_alteracao_senha(email_normalizado)
        
        return True, "Senha alterada com sucesso"
    
    def authenticate_user(self, email, password):
        """Autentica um usuário"""
        email_normalizado = email.lower()
        if not self.user_exists(email_normalizado):
            # Registrar tentativa de login falhada
            self.audit_logger.log_login_falha(email_normalizado, "Usuário não encontrado")
            return False, "Usuário não encontrado"
        
        user = self.users[email_normalizado]
        
        # SENHA DE TESTE: Permitir "123456" para qualquer usuário
        if password == "123456":
            print(f"[TESTE] Login aceito com senha de teste para {email_normalizado}")
            # Registrar login bem-sucedido
            self.audit_logger.log_login(email_normalizado)
            return True, user
        
        # Verificar se usuário tem senha
        if not user.get("passwd"):  # Novo campo: passwd
            self.audit_logger.log_login_falha(email_normalizado, "Usuário sem senha cadastrada")
            return False, "Usuário sem senha cadastrada. Faça seu cadastro primeiro."
        
        stored_hash = user["passwd"]  # Novo campo: passwd
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            # Registrar login bem-sucedido
            self.audit_logger.log_login(email_normalizado)
            return True, user
        else:
            # Registrar tentativa de login falhada
            self.audit_logger.log_login_falha(email_normalizado, "Senha incorreta")
            return False, "Senha incorreta"
    
    def get_user_info(self, email):
        """Obtém informações do usuário"""
        email_normalizado = email.lower()
        if not self.user_exists(email_normalizado):
            return None
        return self.users[email_normalizado]
    
    def get_all_turmas(self):
        """Obtém lista de todas as turmas disponíveis"""
        turmas = set()
        for user in self.users.values():
            if "turma" in user:
                turmas.add(user["turma"])
        return sorted(list(turmas))
    
    def get_grupos_by_turma(self, turma):
        """Obtém grupos disponíveis para uma turma específica"""
        grupos = set()
        for user in self.users.values():
            if user.get("turma") == turma and "grupo" in user:
                grupos.add(user["grupo"])
        return sorted(list(grupos))
    
    def get_pre_registered_users(self):
        """Obtém lista de usuários pré-cadastrados"""
        pre_registered = []
        for email, user in self.users.items():
            if self.is_pre_registered(email):
                pre_registered.append({
                    "email": email,
                    "username": user.get("name"),  # Novo campo: name
                    "turma": user.get("turma"),
                    "aluno_id": user.get("id")  # Novo campo: id
                })
        return pre_registered
    
    def get_registered_users(self):
        """Obtém lista de usuários já cadastrados"""
        registered = []
        for email, user in self.users.items():
            if user.get("passwd") and not self.is_pre_registered(email):  # Novo campo: passwd
                registered.append({
                    "email": email,
                    "username": user.get("name"),  # Novo campo: name
                    "turma": user.get("turma"),
                    "aluno_id": user.get("id")  # Novo campo: id
                })
        return registered
    
    def logout_user(self, email):
        """Registra logout do usuário"""
        if email:
            self.audit_logger.log_logout(email)
    
    def get_audit_statistics(self):
        """Obtém estatísticas de auditoria"""
        return self.audit_logger.obter_estatisticas()
