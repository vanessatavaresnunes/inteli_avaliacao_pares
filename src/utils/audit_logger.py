import json
import datetime
from pathlib import Path
from typing import Dict, Any

class AuditLogger:
    """Sistema de auditoria para rastrear ações dos usuários"""
    
    def __init__(self):
        self.audit_dir = Path("data/auditoria")
        self.audit_dir.mkdir(exist_ok=True)
        self.audit_file = self.audit_dir / "audit_log.json"
        self._load_audit_log()
    
    def _load_audit_log(self):
        """Carrega log de auditoria existente"""
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    self.audit_log = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.audit_log = []
        else:
            self.audit_log = []
    
    def _save_audit_log(self):
        """Salva log de auditoria"""
        with open(self.audit_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, indent=2, ensure_ascii=False)
    
    def log_cadastro(self, email: str, username: str, turma: str, grupo: str, ip_address: str = "N/A"):
        """Registra cadastro de novo usuário"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "acao": "CADASTRO",
            "email": email,
            "username": username,
            "turma": turma,
            "grupo": grupo,
            "ip_address": ip_address,
            "status": "SUCESSO"
        }
        self.audit_log.append(log_entry)
        self._save_audit_log()
    
    def log_login(self, email: str, ip_address: str = "N/A"):
        """Registra login de usuário"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "acao": "LOGIN",
            "email": email,
            "ip_address": ip_address,
            "status": "SUCESSO"
        }
        self.audit_log.append(log_entry)
        self._save_audit_log()
    
    def log_login_falha(self, email: str, motivo: str, ip_address: str = "N/A"):
        """Registra tentativa de login falhada"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "acao": "LOGIN_FALHA",
            "email": email,
            "motivo": motivo,
            "ip_address": ip_address,
            "status": "FALHA"
        }
        self.audit_log.append(log_entry)
        self._save_audit_log()
    
    def log_alteracao_senha(self, email: str, ip_address: str = "N/A"):
        """Registra alteração de senha"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "acao": "ALTERACAO_SENHA",
            "email": email,
            "ip_address": ip_address,
            "status": "SUCESSO"
        }
        self.audit_log.append(log_entry)
        self._save_audit_log()
    
    def log_logout(self, email: str, ip_address: str = "N/A"):
        """Registra logout de usuário"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "acao": "LOGOUT",
            "email": email,
            "ip_address": ip_address,
            "status": "SUCESSO"
        }
        self.audit_log.append(log_entry)
        self._save_audit_log()
    
    def log_avaliacao(self, email_avaliador: str, turma: str, grupo: str, sprint: str, ip_address: str = "N/A"):
        """Registra envio de avaliação"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "acao": "ENVIO_AVALIACAO",
            "email_avaliador": email_avaliador,
            "turma": turma,
            "grupo": grupo,
            "sprint": sprint,
            "ip_address": ip_address,
            "status": "SUCESSO"
        }
        self.audit_log.append(log_entry)
        self._save_audit_log()
    
    def obter_log_por_email(self, email: str) -> list:
        """Obtém log de auditoria para um email específico"""
        return [entry for entry in self.audit_log if entry.get('email') == email]
    
    def obter_log_por_acao(self, acao: str) -> list:
        """Obtém log de auditoria para uma ação específica"""
        return [entry for entry in self.audit_log if entry.get('acao') == acao]
    
    def obter_log_por_periodo(self, inicio: str, fim: str) -> list:
        """Obtém log de auditoria por período"""
        inicio_dt = datetime.datetime.fromisoformat(inicio)
        fim_dt = datetime.datetime.fromisoformat(fim)
        
        return [
            entry for entry in self.audit_log
            if inicio_dt <= datetime.datetime.fromisoformat(entry['timestamp']) <= fim_dt
        ]
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do log de auditoria"""
        total_entradas = len(self.audit_log)
        acoes = {}
        usuarios_unicos = set()
        
        for entry in self.audit_log:
            acao = entry.get('acao', 'DESCONHECIDA')
            acoes[acao] = acoes.get(acao, 0) + 1
            
            if 'email' in entry:
                usuarios_unicos.add(entry['email'])
        
        return {
            "total_entradas": total_entradas,
            "usuarios_unicos": len(usuarios_unicos),
            "acoes": acoes,
            "primeira_entrada": self.audit_log[0]['timestamp'] if self.audit_log else None,
            "ultima_entrada": self.audit_log[-1]['timestamp'] if self.audit_log else None
        }

