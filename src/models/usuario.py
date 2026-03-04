"""
Modelo de dados para usuários e configurações do sistema.
Responsável por gerenciar dados de alunos, times e configurações.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import unicodedata


@dataclass
class Configuracao:
    """Classe que representa as configurações do sistema"""
    nota_minima: int
    nota_maxima: int
    diretorio_dados: str


class UsuarioModel:
    """Modelo responsável por gerenciar dados de usuários e configurações"""
    
    def __init__(self, diretorio_config: str = "data"):
        """
        Inicializa o modelo carregando dados dos arquivos JSON
        
        Args:
            diretorio_config: Diretório onde estão os arquivos de configuração
        """
        self.diretorio_config = diretorio_config
        self.turma_atual = None
        self.alunos = {}
        self.eixos = self._carregar_eixos()
        self.config = self._carregar_configuracao()
        
        # Carregar dados iniciais de alunos (sem turma específica)
        try:
            self.alunos = self._carregar_alunos()
        except Exception as e:
            print(f"Erro ao carregar dados iniciais de alunos: {e}")
            self.alunos = {}

    def obter_turmas(self, periodo: str = "2026-1A") -> list:
        """
        Retorna as turmas disponíveis baseadas no arquivo alunos.json principal.
        
        Args:
            periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
        """
        try:
            # Carregar o arquivo alunos.json principal
            caminho_arquivo = Path(self.diretorio_config) / "alunos.json"
            if caminho_arquivo.exists():
                with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                    dados = json.load(arquivo)
                    # Nova estrutura: {periodo: {T09: {...}, T13: {...}}}
                    if periodo in dados and isinstance(dados[periodo], dict):
                        return list(dados[periodo].keys())  # Retorna as turmas (T09, T13, etc.)
            return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar turmas do arquivo alunos.json: {e}")
            return []

    def _carregar_alunos(self, turma: str = None, periodo: str = "2026-1A") -> Dict[str, List[Dict[str, str]]]:
        """
        Carrega dados dos alunos do arquivo alunos.json principal.
        
        Args:
            turma: Turma específica (opcional)
            periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
        """
        try:
            caminho_arquivo = Path(self.diretorio_config) / "alunos.json"
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
                
                # Nova estrutura: {periodo: {T09: {...}, T13: {...}}}
                if periodo in dados:
                    periodo_data = dados[periodo]
                    
                    # Se uma turma específica foi solicitada, retorna apenas ela
                    if turma and turma in periodo_data:
                        return {turma: periodo_data[turma]}
                    
                    # Se não foi especificada turma, retorna todas do período
                    return periodo_data
                
                return {}
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar alunos do arquivo alunos.json: {e}")
            return {}

    def set_turma(self, turma: str):
        """Define a turma atual e carrega os alunos dessa turma."""
        self.turma_atual = turma
        self.alunos = self._carregar_alunos(turma)

    def validar_senha(self, time: str, aluno: str, senha: str) -> bool:
        """
        Valida a senha de um aluno
        
        Args:
            time: Nome do time
            aluno: Nome do aluno
            senha: Senha a ser verificada
            
        Returns:
            True se a senha estiver correta, False caso contrário
        """
        if time in self.alunos:
            for a in self.alunos[time]:
                if a['nome'] == aluno and a['senha'] == senha:
                    return True
        return False
    
    def _carregar_eixos(self) -> List[Dict[str, any]]:
        """Carrega eixos de avaliação do arquivo JSON"""
        try:
            caminho_arquivo = Path(self.diretorio_config) / "eixos.json"
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                eixos_data = json.load(arquivo)
                for eixo in eixos_data:
                    eixo['nome'] = unicodedata.normalize('NFC', eixo['nome'])
                    eixo['descricao'] = unicodedata.normalize('NFC', eixo['descricao'])
                    if 'observacoes' in eixo:
                        eixo['observacoes'] = [unicodedata.normalize('NFC', obs) for obs in eixo['observacoes']]
                return eixos_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar eixos.json: {e}")
            return []
    
    def _carregar_configuracao(self) -> Dict:
        """Carrega configurações do sistema do arquivo JSON"""
        try:
            caminho_arquivo = Path(self.diretorio_config) / "config.json"
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                return json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar config.json: {e}")
            return {"nota_minima": 0, "regra_nota_maxima": "N/2"}
    
    def calcular_nota_maxima(self, num_integrantes_grupo: int) -> int:
        """
        Calcula a nota máxima dinamicamente baseada no número de integrantes do grupo.
        
        Regra híbrida:
        - Grupos de 2-3 integrantes: usa N/2+1 (parte inteira de N/2 + 1)
        - Grupos de 4+ integrantes: usa N/2 (parte inteira de N/2)
        
        Args:
            num_integrantes_grupo: Número de integrantes no grupo
            
        Returns:
            Nota máxima permitida para o grupo
        """
        config = self._carregar_configuracao()
        regra = config.get('regra_nota_maxima', 'hibrida')
        
        if regra == 'N/2':
            return max(1, num_integrantes_grupo // 2)
        elif regra == 'N/2+1':
            # Regra N/2+1: parte inteira de N/2 + 1
            return max(1, (num_integrantes_grupo // 2) + 1)
        elif regra == 'hibrida':
            # Regra híbrida: N/2+1 para grupos pequenos, N/2 para grupos grandes
            if num_integrantes_grupo <= 3:
                # Grupos de 2-3: N/2+1
                return max(1, (num_integrantes_grupo // 2) + 1)
            else:
                # Grupos de 4+: N/2
                return max(1, num_integrantes_grupo // 2)
        elif regra == 'N':
            return num_integrantes_grupo
        elif regra == 'N-1':
            return max(1, num_integrantes_grupo - 1)
        else:
            # Fallback para regras customizadas ou valor padrão
            try:
                # Tenta avaliar expressões matemáticas simples como "N/2", "N-1", etc.
                import re
                if 'N' in regra:
                    # Substitui N pelo número de integrantes e avalia
                    expressao = regra.replace('N', str(num_integrantes_grupo))
                    # Remove caracteres perigosos e avalia apenas operações básicas
                    if re.match(r'^[\d\+\-\*\/\(\)\s]+$', expressao):
                        return max(1, int(eval(expressao)))
                    else:
                        raise ValueError("Expressão inválida")
                else:
                    # Se não tem N, tenta converter para int
                    return max(1, int(regra))
            except (ValueError, SyntaxError):
                # Fallback para regra híbrida
                if num_integrantes_grupo <= 3:
                    return max(1, (num_integrantes_grupo // 2) + 1)
                else:
                    return max(1, num_integrantes_grupo // 2)
    
    def obter_configuracao_notas(self, num_integrantes_grupo: int = None) -> Dict:
        """
        Retorna configuração de notas com nota máxima calculada dinamicamente.
        
        Args:
            num_integrantes_grupo: Número de integrantes no grupo (opcional)
            
        Returns:
            Dicionário com nota_minima e nota_maxima
        """
        config = self._carregar_configuracao()
        
        if num_integrantes_grupo is not None:
            nota_maxima = self.calcular_nota_maxima(num_integrantes_grupo)
        else:
            # Fallback para valor padrão se não especificado
            nota_maxima = 3
        
        return {
            "nota_minima": config.get('nota_minima', 0),
            "nota_maxima": nota_maxima
        }
    
    def obter_times(self, turma: str = None, periodo: str = "2026-1A") -> List[str]:
        """
        Retorna lista de times disponíveis para a turma informada ou atual.
        
        Args:
            turma: Turma específica (opcional)
            periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
        """
        if turma:
            alunos = self._carregar_alunos(turma, periodo)
            return list(alunos.keys())
        return list(self.alunos.keys())

    def obter_alunos_por_time(self, time: str, turma: str = None, periodo: str = "2026-1A") -> List[Dict[str, any]]:
        """
        Retorna lista de alunos de um time específico para a turma informada ou atual.
        
        Args:
            time: Nome do time
            turma: Turma específica (opcional)
            periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
        """
        if turma:
            alunos = self._carregar_alunos(turma, periodo)
            return alunos.get(time, [])
        return self.alunos.get(time, [])
    
    def obter_alunos_time_excluindo(self, time: str, aluno_excluir: str, turma: str = None, periodo: str = "2026-1A") -> List[Dict[str, any]]:
        """
        Retorna lista de alunos de um time excluindo um aluno específico
        
        Args:
            time: Nome do time
            aluno_excluir: Nome do aluno a ser excluído
            turma: Turma a ser considerada (opcional)
            periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
            
        Returns:
            Lista de alunos do time sem o aluno excluído
        """
        alunos_time = self.obter_alunos_por_time(time, turma, periodo)
        return [aluno for aluno in alunos_time if aluno['nome'] != aluno_excluir]
    
    def obter_aluno_por_nome(self, nome_aluno: str) -> Optional[Dict[str, any]]:
        """
        Retorna os dados de um aluno pelo nome.

        Args:
            nome_aluno: Nome do aluno a ser buscado.

        Returns:
            Dicionário com os dados do aluno ou None se não encontrado.
        """
        for time in self.alunos.values():
            # Verificar se time é uma lista
            if not isinstance(time, list):
                continue
            for aluno in time:
                # Verificar se aluno é um dicionário
                if not isinstance(aluno, dict):
                    continue
                if 'nome' in aluno and unicodedata.normalize('NFC', str(aluno['nome'])) == unicodedata.normalize('NFC', nome_aluno):
                    return aluno
        return None

    def obter_aluno_por_id(self, id_aluno: int) -> Optional[Dict[str, any]]:
        """
        Retorna os dados de um aluno pelo ID.

        Args:
            id_aluno: ID do aluno a ser buscado.

        Returns:
            Dicionário com os dados do aluno ou None se não encontrado.
        """
        for time in self.alunos.values():
            for aluno in time:
                if aluno['id'] == id_aluno:
                    return aluno
        return None

    def obter_id_aluno(self, nome_aluno: str) -> Optional[int]:
        """
        Retorna o ID de um aluno pelo nome.

        Args:
            nome_aluno: Nome do aluno.

        Returns:
            ID do aluno ou None se não encontrado.
        """
        aluno = self.obter_aluno_por_nome(nome_aluno)
        return aluno['id'] if aluno else None

    def obter_nome_aluno(self, id_aluno: int, turma: str = None) -> Optional[str]:
        """
        Retorna o nome de um aluno pelo ID, considerando a turma se informada.
        Args:
            id_aluno: ID do aluno.
            turma: Turma a ser considerada (opcional)
        Returns:
            Nome do aluno ou None se não encontrado.
        """
        try:
            print(f"🔍 Buscando aluno ID {id_aluno} na turma {turma}")
            
            # Carregar dados de usuários
            caminho_usuarios = Path(self.diretorio_config) / "usuarios" / "usuarios.json"
            if not caminho_usuarios.exists():
                print(f"❌ Arquivo usuarios.json não encontrado em {caminho_usuarios}")
                return None
            
            with open(caminho_usuarios, 'r', encoding='utf-8') as arquivo:
                usuarios = json.load(arquivo)
            
            # Buscar aluno pelo ID
            for email, dados in usuarios.items():
                if dados.get('id') == id_aluno:
                    nome_aluno = dados.get('name')
                    turma_aluno = dados.get('turma')
                    
                    print(f"✅ Aluno encontrado: ID {id_aluno} -> Nome: '{nome_aluno}', Turma: {turma_aluno}")
                    
                    # Se uma turma específica foi solicitada, verificar se corresponde
                    if turma and turma_aluno != turma:
                        print(f"⚠️ Aluno ID {id_aluno} pertence à turma {turma_aluno}, mas foi solicitada a turma {turma}")
                        continue
                    
                    return nome_aluno
            
            print(f"❌ Aluno ID {id_aluno} não encontrado no arquivo usuarios.json")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar aluno ID {id_aluno} na turma {turma}: {e}")
            return None

    def obter_eixos(self) -> List[Dict[str, any]]:
        """Retorna lista de eixos de avaliação com nome, descrição e observações"""
        return self.eixos.copy()
    
    def obter_nomes_eixos(self) -> List[str]:
        """Retorna lista apenas com os nomes dos eixos de avaliação"""
        return [eixo["nome"] for eixo in self.eixos]
    
    def obter_descricao_eixo(self, nome_eixo: str) -> str:
        """
        Retorna a descrição de um eixo específico
        
        Args:
            nome_eixo: Nome do eixo
            
        Returns:
            Descrição do eixo ou string vazia se não encontrado
        """
        for eixo in self.eixos:
            if unicodedata.normalize('NFC', eixo["nome"]) == unicodedata.normalize('NFC', nome_eixo):
                return eixo["descricao"]
        return ""
    
    def obter_observacoes_eixo(self, nome_eixo: str) -> List[str]:
        """
        Retorna as observações de um eixo específico
        
        Args:
            nome_eixo: Nome do eixo
            
        Returns:
            Lista de observações do eixo ou lista vazia se não encontrado
        """
        for eixo in self.eixos:
            if unicodedata.normalize('NFC', eixo["nome"]) == unicodedata.normalize('NFC', nome_eixo):
                return eixo.get("observacoes", [])
        return []
    
    def obter_configuracao(self) -> Dict:
        """Retorna configurações do sistema"""
        return self.config
    
    def validar_time(self, time: str) -> bool:
        """
        Valida se um time existe
        
        Args:
            time: Nome do time
            
        Returns:
            True se o time existe, False caso contrário
        """
        return time in self.alunos
    
    def validar_aluno(self, time: str, aluno: str) -> bool:
        """
        Valida se um aluno pertence a um time
        
        Args:
            time: Nome do time
            aluno: Nome do aluno
            
        Returns:
            True se o aluno pertence ao time, False caso contrário
        """
        if time in self.alunos:
            return any(unicodedata.normalize('NFC', a['nome']) == unicodedata.normalize('NFC', aluno) for a in self.alunos[time])
        return False
