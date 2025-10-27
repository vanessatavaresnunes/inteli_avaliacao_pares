import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class MatriculaValidator:
    """Classe para validar matrículas de alunos contra a lista oficial"""
    
    def __init__(self, periodo: str = None):
        """
        Inicializa o validador de matrículas
        
        Args:
            periodo: Período acadêmico (ex: "2025-2A", "2025-2B"). Se None, usa PERIODO_ATUAL
        """
        self.alunos_file = Path("data/alunos.json")
        self.usuarios_file = Path("data/usuarios/usuarios.json")
        
        # Se não especificado, usar o período atual da variável de ambiente
        if periodo is None:
            periodo = os.getenv("PERIODO_ATUAL", "2025-2A")
        
        self.periodo = periodo
        self.alunos_data = self._load_alunos()
        self.usuarios_data = self._load_usuarios()
    
    def _load_alunos(self) -> Dict:
        """
        Carrega dados dos alunos do arquivo JSON otimizado.
        Nova estrutura: {periodo: {T09: {...}, T13: {...}}}
        """
        if self.alunos_file.exists():
            try:
                with open(self.alunos_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    # Se for a nova estrutura com períodos, extrair dados do período
                    if self.periodo in dados and isinstance(dados[self.periodo], dict):
                        return dados[self.periodo]
                    return {}
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _load_usuarios(self) -> Dict:
        """Carrega dados dos usuários para obter informações completas"""
        if self.usuarios_file.exists():
            try:
                with open(self.usuarios_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def validar_email_matricula(self, email: str) -> Tuple[bool, Optional[Dict]]:
        """
        Valida se um email está na lista oficial de matrícula
        
        Args:
            email: Email a ser validado
            
        Returns:
            (é_válido, dados_aluno) ou (False, None)
        """
        from .email_validator import is_valid_inteli_email
        if not email or not is_valid_inteli_email(email):
            return False, None
        
        # Buscar o usuário nos dados de usuários
        if email in self.usuarios_data:
            usuario = self.usuarios_data[email]
            turma = usuario.get('turma')
            aluno_id = usuario.get('id')
            
            # Buscar o grupo no arquivo alunos.json
            grupo = self._encontrar_grupo_por_id(turma, aluno_id)
            
            return True, {
                'turma': turma,
                'grupo': grupo,
                'id': aluno_id,
                'nome': usuario.get('name'),
                'email': email,
                'passwd': usuario.get('passwd', '')
            }
        
        return False, None
    
    def obter_turmas_disponiveis(self) -> List[str]:
        """Retorna lista de turmas disponíveis"""
        return list(self.alunos_data.keys())
    
    def obter_grupos_por_turma(self, turma: str) -> List[str]:
        """Retorna grupos disponíveis para uma turma específica"""
        if turma in self.alunos_data:
            return list(self.alunos_data[turma].keys())
        return []
    
    def obter_alunos_por_grupo(self, turma: str, grupo: str) -> List[Dict]:
        """Retorna alunos de um grupo específico com dados completos"""
        if turma not in self.alunos_data or grupo not in self.alunos_data[turma]:
            return []
        
        alunos_ids = self.alunos_data[turma][grupo]
        alunos_completos = []
        
        # Buscar dados completos dos usuários
        for email, usuario in self.usuarios_data.items():
            if (usuario.get('turma') == turma and 
                usuario.get('id') in alunos_ids):
                alunos_completos.append({
                    'id': usuario.get('id'),
                    'nome': usuario.get('name'),
                    'email': email,
                    'passwd': usuario.get('passwd', '')
                })
        
        return sorted(alunos_completos, key=lambda x: x['id'])
    
    def _encontrar_grupo_por_id(self, turma: str, aluno_id: int) -> str:
        """
        Encontra o grupo de um aluno baseado na turma e ID
        
        Args:
            turma: Turma do aluno
            aluno_id: ID do aluno
            
        Returns:
            Nome do grupo ou "Grupo não encontrado"
        """
        if turma not in self.alunos_data:
            return "Grupo não encontrado"
        
        for grupo, ids_alunos in self.alunos_data[turma].items():
            if aluno_id in ids_alunos:
                return grupo
        
        return "Grupo não encontrado"
    
    def obter_todas_matriculas(self) -> List[Dict]:
        """Retorna todas as matrículas para auditoria"""
        matriculas = []
        for email, usuario in self.usuarios_data.items():
            if usuario.get('id'):  # Apenas alunos (não professores)
                grupo = self._encontrar_grupo_por_id(usuario.get('turma'), usuario.get('id'))
                matriculas.append({
                    'turma': usuario.get('turma'),
                    'grupo': grupo,
                    'id': usuario.get('id'),
                    'nome': usuario.get('name'),
                    'email': email,
                    'passwd': usuario.get('passwd', '')
                })
        return matriculas
    
    def buscar_aluno_por_email(self, email: str) -> Optional[Dict]:
        """Busca dados completos de um aluno por email"""
        email_normalizado = email.lower()
        if email_normalizado in self.usuarios_data:
            usuario = self.usuarios_data[email_normalizado]
            if usuario.get('id'):  # Apenas alunos
                grupo = self._encontrar_grupo_por_id(usuario.get('turma'), usuario.get('id'))
                return {
                    'turma': usuario.get('turma'),
                    'grupo': grupo,
                    'id': usuario.get('id'),
                    'nome': usuario.get('name'),
                    'email': email_normalizado,
                    'passwd': usuario.get('passwd', '')
                }
        return None
    
    def obter_usuarios_pre_cadastrados(self) -> List[Dict]:
        """Retorna lista de usuários pré-cadastrados (sem senha)"""
        pre_cadastrados = []
        for email, usuario in self.usuarios_data.items():
            if not usuario.get('passwd'):  # Sem senha
                grupo = self._encontrar_grupo_por_id(usuario.get('turma'), usuario.get('id'))
                pre_cadastrados.append({
                    'email': email,
                    'nome': usuario.get('name'),
                    'turma': usuario.get('turma'),
                    'grupo': grupo,
                    'id': usuario.get('id')
                })
        return pre_cadastrados
    
    def obter_usuarios_cadastrados(self) -> List[Dict]:
        """Retorna lista de usuários já cadastrados (com senha)"""
        cadastrados = []
        for email, usuario in self.usuarios_data.items():
            if usuario.get('passwd'):  # Com senha
                grupo = self._encontrar_grupo_por_id(usuario.get('turma'), usuario.get('id'))
                cadastrados.append({
                    'email': email,
                    'nome': usuario.get('name'),
                    'turma': usuario.get('turma'),
                    'grupo': grupo,
                    'id': usuario.get('id')
                })
        return cadastrados
