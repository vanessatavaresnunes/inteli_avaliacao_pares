"""
Controller para gerenciar a lógica de negócio das avaliações.
Responsável por coordenar entre modelos e views.
"""

from typing import Dict, List, Optional, Tuple
import streamlit as st
import json
from datetime import datetime, timedelta
from src.models.avaliacao import AvaliacaoModel
from src.models.usuario import UsuarioModel
from src.utils.matricula_validator import MatriculaValidator


class AvaliacaoController:
    """Controller responsável por gerenciar a lógica de avaliações"""
    
    def __init__(self):
        self.avaliacao_model = AvaliacaoModel()
        self.usuario_model = UsuarioModel()
        self.matricula_validator = MatriculaValidator()
    
    def inicializar_sessao(self):
        """Inicializa a sessão do Streamlit se necessário"""
        # Só inicializar se o usuário estiver autenticado
        if st.session_state.get('user_authenticated', False):
            if 'avaliacoes_temp' not in st.session_state:
                st.session_state.avaliacoes_temp = {}
            
            if 'logado' not in st.session_state:
                st.session_state.logado = False

            if 'validation_messages' not in st.session_state:
                st.session_state.validation_messages = {
                    'soma_notas': {'is_valid': True, 'messages': [], 'details': {}},
                    'notas_individuais': {'is_valid': True, 'messages': []},
                    'feedbacks_preenchidos': {'is_valid': True, 'messages': []},
                    'feedbacks_unicos': {'is_valid': True, 'messages': []},
                    'conteudo_feedbacks': {'is_valid': True, 'messages': []}
                }
    
    def fazer_login(self, time: str, aluno: str, senha: str, turma: str = None) -> bool:
        """
        Realiza o login do usuário
        
        Args:
            time: Nome do time
            aluno: Nome do aluno
            senha: Senha do aluno
            turma: Turma selecionada
            
        Returns:
            True se login bem-sucedido, False caso contrário
        """
        self.usuario_model.set_turma(turma)
        if self.usuario_model.validar_time(time) and \
           self.usuario_model.validar_aluno(time, aluno) and \
           self.usuario_model.validar_senha(time, aluno, senha):
            st.session_state.logado = True
            st.session_state.aluno_atual = aluno
            st.session_state.aluno_id_atual = self.usuario_model.obter_id_aluno(aluno)
            st.session_state.time_atual = time
            st.session_state.turma_atual = turma
            return True
        return False
    
    def fazer_logout(self):
        """Realiza o logout do usuário"""
        # Limpar todas as variáveis de autenticação
        st.session_state.logado = False
        st.session_state.user_authenticated = False
        
        # Limpar dados do usuário
        if 'aluno_atual' in st.session_state:
            del st.session_state.aluno_atual
        if 'aluno_id_atual' in st.session_state:
            del st.session_state.aluno_id_atual
        if 'time_atual' in st.session_state:
            del st.session_state.time_atual
        if 'turma_atual' in st.session_state:
            del st.session_state.turma_atual
        if 'avaliacoes_temp' in st.session_state:
            del st.session_state.avaliacoes_temp
        
        # Limpar dados de autenticação
        if 'user_email' in st.session_state:
            del st.session_state.user_email
        if 'user_name' in st.session_state:
            del st.session_state.user_name
        if 'user_turma' in st.session_state:
            del st.session_state.user_turma
        if 'user_grupo' in st.session_state:
            del st.session_state.user_grupo
        
        # Limpar outras variáveis de sessão
        if 'sprint_atual' in st.session_state:
            del st.session_state.sprint_atual
        if 'validation_messages' in st.session_state:
            del st.session_state.validation_messages
        
        # Registrar logout na auditoria se possível
        try:
            if hasattr(self, 'matricula_validator'):
                # Tentar registrar logout (email pode não estar mais disponível)
                pass
        except:
            pass
        
        # Forçar rerun para voltar à tela de login
        st.rerun()
    
    def esta_logado(self) -> bool:
        """
        Verifica se o usuário está logado
        
        Returns:
            True se logado, False caso contrário
        """
        return st.session_state.get('logado', False)
    
    def obter_dados_usuario_atual(self) -> Tuple[int, str]:
        """
        Obtém dados do usuário atualmente logado
        
        Returns:
            Tupla com (id_aluno, time)
        """
        return st.session_state.aluno_id_atual, st.session_state.time_atual
    
    def obter_alunos_para_avaliar(self) -> List[Dict[str, any]]:
        """
        Obtém lista de alunos que podem ser avaliados pelo usuário atual
        Returns:
            Lista de alunos do mesmo time (excluindo o próprio)
        """
        aluno_atual = st.session_state.aluno_atual
        time_atual = st.session_state.time_atual
        turma_atual = st.session_state.get('turma_atual', None)
        
        print(f"🔍 obter_alunos_para_avaliar:")
        print(f"  aluno_atual: {aluno_atual}")
        print(f"  time_atual: {time_atual}")
        print(f"  turma_atual: {turma_atual}")
        
        # Usar MatriculaValidator para obter alunos do grupo
        if turma_atual and time_atual:
            try:
                alunos_grupo = self.matricula_validator.obter_alunos_por_grupo(turma_atual, time_atual)
                print(f"  MatriculaValidator retornou: {len(alunos_grupo)} alunos")
                print(f"  Dados dos alunos: {alunos_grupo}")
                
                # Excluir o aluno atual da lista
                alunos_para_avaliar = [aluno for aluno in alunos_grupo if aluno['nome'] != aluno_atual]
                print(f"  Após exclusão: {len(alunos_para_avaliar)} alunos")
                print(f"  Alunos para avaliar: {alunos_para_avaliar}")
                
                return alunos_para_avaliar
            except Exception as e:
                print(f"  ❌ Erro no MatriculaValidator: {e}")
                # Fallback para o método antigo
                return self.usuario_model.obter_alunos_time_excluindo(time_atual, aluno_atual, turma=turma_atual)
        
        # Fallback para o método antigo se necessário
        print(f"  Usando fallback do modelo")
        return self.usuario_model.obter_alunos_time_excluindo(time_atual, aluno_atual, turma=turma_atual)
    
    def inicializar_avaliacao_aluno(self, aluno: Dict[str, any]):
        """
        Inicializa a estrutura de avaliação para um aluno
        
        Args:
            aluno: Dicionário com dados do aluno
        """
        aluno_id = aluno['id']
        if aluno_id not in st.session_state.avaliacoes_temp:
            nomes_eixos = self.obter_nomes_eixos()
            st.session_state.avaliacoes_temp[aluno_id] = {
                'notas': [0] * len(nomes_eixos),
                'feedbacks': [''] * len(nomes_eixos)
            }
    
    def atualizar_nota(self, aluno_id: int, eixo_index: int):
        """
        Atualiza a nota de um aluno em um eixo específico
        
        Args:
            aluno_id: ID do aluno
            eixo_index: Índice do eixo (0-2)
        """
        key = f"nota_{aluno_id}_{eixo_index}"
        nota = st.session_state[key]
        if aluno_id in st.session_state.avaliacoes_temp:
            st.session_state.avaliacoes_temp[aluno_id]['notas'][eixo_index] = nota
        self.validar_avaliacoes()
    
    def atualizar_feedback(self, aluno_id: int, eixo_index: int):
        """
        Atualiza o feedback de um aluno para um eixo específico
        
        Args:
            aluno_id: ID do aluno
            eixo_index: Índice do eixo
        """
        key = f"feedback_{aluno_id}_{eixo_index}"
        feedback = st.session_state[key]
        if aluno_id in st.session_state.avaliacoes_temp:
            st.session_state.avaliacoes_temp[aluno_id]['feedbacks'][eixo_index] = feedback
        self.validar_avaliacoes()
    
    def validar_avaliacoes(self) -> Dict[str, any]:
        """
        Valida todas as avaliações atuais.

        Returns:
            Dicionário com os resultados de cada validação.
        """
        alunos_time = self.obter_alunos_para_avaliar()
        nomes_eixos = self.obter_nomes_eixos()
        
        # Calcular número total de integrantes no grupo (incluindo o avaliador)
        num_integrantes_grupo = len(alunos_time) + 1
        
        # Usar a nova configuração dinâmica de notas com o número correto de integrantes
        config_notas = self.obter_configuracao_notas(num_integrantes_grupo)
        
        # Criar config compatível com o modelo antigo
        config = {
            'nota_minima': config_notas['nota_minima'],
            'nota_maxima': config_notas['nota_maxima']
        }

        # Garante que a avaliação temporária exista para todos os alunos
        for aluno in alunos_time:
            self.inicializar_avaliacao_aluno(aluno)

        # Initialize validation messages structure
        st.session_state.validation_messages = {
            'soma_notas': {'is_valid': True, 'messages': [], 'details': {}},
            'notas_individuais': {'is_valid': True, 'messages': []},
            'feedbacks_preenchidos': {'is_valid': True, 'messages': []},
            'feedbacks_unicos': {'is_valid': True, 'messages': []},
            'conteudo_feedbacks': {'is_valid': True, 'messages': []}
        }

        # Perform validations
        validacoes = self.avaliacao_model.validar_avaliacoes(
            st.session_state.avaliacoes_temp,
            [aluno['id'] for aluno in alunos_time],
            nomes_eixos,
            config,
            num_integrantes_grupo
        )

        # Store messages based on validation results
        # Validação da soma de notas por eixo
        soma_notas_validas_geral = True
        for eixo, detalhes in validacoes['soma_notas'].items():
            st.session_state.validation_messages['soma_notas']['details'][eixo] = { # Store details for each axis
                'soma_atual': detalhes['soma_atual'],
                'soma_esperada': detalhes['soma_esperada']
            }
            if not detalhes['valido']:
                soma_notas_validas_geral = False
                diferenca = detalhes['soma_atual'] - detalhes['soma_esperada']
                if diferenca > 0:
                    st.session_state.validation_messages['soma_notas']['messages'].append(
                        f"A soma das notas para o eixo '{eixo}' excedeu em {diferenca} ponto(s). Soma atual: {detalhes['soma_atual']}, Esperado: {detalhes['soma_esperada']}."
                    )
                else:
                    st.session_state.validation_messages['soma_notas']['messages'].append(
                        f"A soma das notas para o eixo '{eixo}' está faltando {-diferenca} ponto(s). Soma atual: {detalhes['soma_atual']}, Esperado: {detalhes['soma_esperada']}."
                    )
        st.session_state.validation_messages['soma_notas']['is_valid'] = soma_notas_validas_geral

        # Validação de notas individuais
        if not validacoes['notas_individuais']:
            st.session_state.validation_messages['notas_individuais']['is_valid'] = False
            st.session_state.validation_messages['notas_individuais']['messages'].append(
                "Pelo menos uma nota excede o valor máximo permitido ou a regra N/2."
            )

        # Validação de preenchimento de feedbacks
        if not validacoes['feedbacks_preenchidos']:
            st.session_state.validation_messages['feedbacks_preenchidos']['is_valid'] = False
            st.session_state.validation_messages['feedbacks_preenchidos']['messages'].append(
                "Todos os campos de feedback devem ser preenchidos."
            )

        # Validação de feedbacks únicos
        if not validacoes['feedbacks_unicos']:
            st.session_state.validation_messages['feedbacks_unicos']['is_valid'] = False
            st.session_state.validation_messages['feedbacks_unicos']['messages'].append(
                "Os feedbacks para um mesmo aluno não podem ser iguais."
            )

        # Validação de conteúdo de feedbacks
        if not validacoes['conteudo_feedbacks']:
            st.session_state.validation_messages['conteudo_feedbacks']['is_valid'] = False
            st.session_state.validation_messages['conteudo_feedbacks']['messages'].append(
                "Os feedbacks devem conter pelo menos duas palavras e não podem conter emojis ou caracteres especiais."
            )
        
        return validacoes


    
    def salvar_avaliacoes(self) -> Tuple[bool, str]:
        """
        Salva as avaliações atuais.

        Returns:
            Tupla com (sucesso, mensagem).
        """
        try:
            # Validar antes de salvar
            validacoes = self.validar_avaliacoes()
            mensagens_erro = []

            # Checar soma das notas
            if not all(validacoes['soma_notas'].values()):
                eixos_invalidos = [eixo for eixo, valido in validacoes['soma_notas'].items() if not valido]
                mensagens_erro.append(f"A soma das notas para os eixos {', '.join(eixos_invalidos)} está incorreta.")

            # Checar notas individuais
            if not validacoes['notas_individuais']:
                mensagens_erro.append("Uma ou mais notas excedem o valor máximo permitido.")

            # Checar preenchimento dos feedbacks
            if not validacoes['feedbacks_preenchidos']:
                mensagens_erro.append("Todos os campos de feedback devem ser preenchidos.")

            # Checar feedbacks únicos
            if not validacoes['feedbacks_unicos']:
                mensagens_erro.append("Os feedbacks para um mesmo aluno não podem ser iguais.")

            # Checar conteúdo dos feedbacks
            if not validacoes['conteudo_feedbacks']:
                mensagens_erro.append("Os feedbacks não podem conter emojis ou caracteres especiais.")

            if mensagens_erro:
                return False, "\n".join(mensagens_erro)

            # Salvar avaliações
            aluno_id_atual, time_atual = self.obter_dados_usuario_atual()
            sprint_atual = st.session_state.sprint_atual
            nomes_eixos = self.obter_nomes_eixos()
            nome_avaliador = self.usuario_model.obter_nome_aluno(aluno_id_atual)
            turma_atual = st.session_state.get('turma_atual', None)
            arquivo = self.avaliacao_model.salvar_avaliacoes(
                aluno_id_atual, time_atual, sprint_atual, st.session_state.avaliacoes_temp, nomes_eixos, nome_avaliador, turma=turma_atual
            )

            # Salvar uma cópia para a tela de sucesso
            st.session_state['avaliacoes_temp_salvas'] = st.session_state.avaliacoes_temp.copy()
            # Limpar dados temporários
            del st.session_state.avaliacoes_temp

            # Preparar envio de email em background (não bloqueia o redirecionamento)
            email_usuario = st.session_state.get('user_email')
            if email_usuario:
                # Armazenar informações para envio de email em background
                st.session_state['email_pendente'] = {
                    'email': email_usuario,
                    'id_avaliador': aluno_id_atual
                }
                return True, f"Avaliações salvas com sucesso! Email será enviado para {email_usuario}"
            else:
                return True, f"Avaliações salvas com sucesso! (Aviso: Email não será enviado - Email do usuário não encontrado)"

        except Exception as e:
            return False, f"Erro ao salvar: {str(e)}"
    
    def obter_estatisticas_avaliacoes(self) -> Dict:
        """
        Obtém estatísticas das avaliações salvas
        
        Returns:
            Dicionário com estatísticas
        """
        df = self.avaliacao_model.carregar_dados()
        return self.avaliacao_model.obter_estatisticas(df)
    
    def obter_dados_filtrados(self, time_filtro: str = None, 
                            avaliador_filtro: int = None, 
                            eixo_filtro: str = None) -> 'pd.DataFrame':
        """
        Obtém dados filtrados para visualização
        
        Args:
            time_filtro: Filtro por time
            avaliador_filtro: Filtro por id do avaliador
            eixo_filtro: Filtro por eixo
            
        Returns:
            DataFrame filtrado
        """
        df = self.avaliacao_model.carregar_dados()
        
        if df.empty:
            return df
        
        if time_filtro and time_filtro != 'Todos':
            df = df[df['time'] == time_filtro]
        
        if avaliador_filtro and avaliador_filtro != 'Todos':
            df = df[df['id_avaliador'] == avaliador_filtro]
        
        if eixo_filtro and eixo_filtro != 'Todos':
            df = df[df['eixo'] == eixo_filtro]
        
        return df
    
    def obter_configuracao(self):
        """Obtém configurações do sistema"""
        return self.usuario_model.obter_configuracao()
    
    def obter_configuracao_notas(self, num_integrantes_grupo: int = None):
        """
        Obtém configuração de notas com nota máxima calculada dinamicamente
        
        Args:
            num_integrantes_grupo: Número de integrantes no grupo
            
        Returns:
            Dicionário com nota_minima e nota_maxima
        """
        return self.usuario_model.obter_configuracao_notas(num_integrantes_grupo)
    
    def enviar_avaliacoes_por_email(self, email_usuario: str) -> tuple[bool, str]:
        """
        Envia avaliações do usuário por email
        
        Args:
            email_usuario: Email do usuário para envio
            
        Returns:
            Tupla com (sucesso, mensagem)
        """
        try:
            # Obter dados do usuário
            nome_usuario = st.session_state.get('user_name', 'Usuário')
            grupo_usuario = st.session_state.get('time_atual', 'N/A')
            sprint_atual = st.session_state.get('sprint_atual', 'Sprint Atual')
            aluno_id_atual = st.session_state.get('aluno_id_atual')
            
            print(f"🔍 DEBUG - Dados do usuário:")
            print(f"  - Nome: {nome_usuario}")
            print(f"  - Grupo: {grupo_usuario}")
            print(f"  - Sprint: {sprint_atual}")
            print(f"  - ID do aluno: {aluno_id_atual}")
            print(f"  - Email: {email_usuario}")
            
            if not aluno_id_atual:
                return False, "ID do usuário não encontrado. Faça login novamente."
            
            # Carregar avaliações do usuário (sempre do Supabase)
            print(f"🔄 Carregando dados do Supabase...")
            df = self.avaliacao_model.carregar_dados()
            print(f"🔍 DEBUG - DataFrame carregado:")
            print(f"  - Total de registros: {len(df)}")
            print(f"  - Colunas: {list(df.columns) if not df.empty else 'DataFrame vazio'}")
            
            if df.empty:
                return False, "Nenhum dado encontrado no Supabase. Tente novamente em alguns segundos."
            
            # Verificar se o ID existe nos dados
            if 'id_avaliador' not in df.columns:
                return False, "Erro: Coluna 'id_avaliador' não encontrada nos dados."
            
            ids_disponiveis = df['id_avaliador'].unique()
            print(f"  - IDs de avaliadores únicos: {ids_disponiveis}")
            print(f"  - Procurando por ID: {aluno_id_atual}")
            
            if aluno_id_atual not in ids_disponiveis:
                return False, f"ID {aluno_id_atual} não encontrado nos dados disponíveis. IDs disponíveis: {sorted(ids_disponiveis)}"
            
            avaliacoes_usuario = df[df['id_avaliador'] == aluno_id_atual]
            print(f"🔍 DEBUG - Avaliações encontradas para o usuário: {len(avaliacoes_usuario)}")
            
            if avaliacoes_usuario.empty:
                return False, f"Nenhuma avaliação encontrada para o ID {aluno_id_atual}. Verifique se as avaliações foram salvas corretamente."
            
            # Preparar dados para o email - transformar estrutura de dados
            avaliacoes_data = {
                'sprint': sprint_atual,
                'grupo': grupo_usuario,
                'avaliacoes': []
            }
            
            # Agrupar avaliações por aluno avaliado
            print(f"🔍 DEBUG - Agrupando avaliações por aluno avaliado...")
            avaliacoes_por_aluno = {}
            eixos_processados = set()
            
            for _, row in avaliacoes_usuario.iterrows():
                id_avaliado = row.get('id_avaliado')
                nome_avaliado = row.get('nome_avaliado', 'Aluno')
                eixo = row.get('eixo', '')
                nota = row.get('nota', 0)
                feedback = row.get('feedback', 'N/A')
                
                print(f"  📝 Processando: {nome_avaliado} - {eixo} = {nota}")
                
                if id_avaliado not in avaliacoes_por_aluno:
                    avaliacoes_por_aluno[id_avaliado] = {
                        'aluno_avaliado': nome_avaliado,
                        'nota_eixo1': 0,
                        'nota_eixo2': 0,
                        'nota_eixo3': 0,
                        'feedback_eixo1': 'N/A',
                        'feedback_eixo2': 'N/A',
                        'feedback_eixo3': 'N/A'
                    }
                
                # Mapear eixo para o campo correto (case-insensitive)
                eixo_lower = eixo.lower()
                eixos_processados.add(eixo)
                
                if 'entregas' in eixo_lower and 'reais' in eixo_lower:
                    avaliacoes_por_aluno[id_avaliado]['nota_eixo1'] = nota
                    avaliacoes_por_aluno[id_avaliado]['feedback_eixo1'] = feedback
                    print(f"    ✅ Mapeado para eixo 1")
                elif 'valor' in eixo_lower and 'percebido' in eixo_lower:
                    avaliacoes_por_aluno[id_avaliado]['nota_eixo2'] = nota
                    avaliacoes_por_aluno[id_avaliado]['feedback_eixo2'] = feedback
                    print(f"    ✅ Mapeado para eixo 2")
                elif 'caixa' in eixo_lower and 'ferramentas' in eixo_lower:
                    avaliacoes_por_aluno[id_avaliado]['nota_eixo3'] = nota
                    avaliacoes_por_aluno[id_avaliado]['feedback_eixo3'] = feedback
                    print(f"    ✅ Mapeado para eixo 3")
                else:
                    print(f"    ❌ Eixo não reconhecido: {eixo}")
            
            print(f"🔍 DEBUG - Eixos processados: {eixos_processados}")
            print(f"🔍 DEBUG - Alunos agrupados: {len(avaliacoes_por_aluno)}")
            
            # Converter para lista
            avaliacoes_data['avaliacoes'] = list(avaliacoes_por_aluno.values())
            
            # Verificação final antes do envio
            if not avaliacoes_data['avaliacoes']:
                return False, "Nenhuma avaliação válida encontrada para enviar por email."
            
            print(f"🔍 DEBUG - Dados preparados para email:")
            print(f"  - Sprint: {avaliacoes_data['sprint']}")
            print(f"  - Grupo: {avaliacoes_data['grupo']}")
            print(f"  - Avaliações: {len(avaliacoes_data['avaliacoes'])}")
            
            # Enviar email
            print(f"📤 Enviando email para {email_usuario}...")
            from src.utils.email_service import EmailService
            email_service = EmailService()
            success, message = email_service.enviar_avaliacoes(
                email_usuario, nome_usuario, avaliacoes_data
            )
            
            print(f"📊 Resultado do envio: {success} - {message}")
            return success, message
            
        except Exception as e:
            return False, f"Erro ao preparar email: {str(e)}"
    
    def processar_emails_pendentes(self):
        """
        Processa emails pendentes em background
        """
        if 'email_pendente' in st.session_state:
            email_info = st.session_state['email_pendente']
            try:
                # Aguardar consolidação dos dados
                import time
                print(f"⏳ Aguardando consolidação dos dados antes do envio de email...")
                time.sleep(2)  # Aguardar 2 segundos para consolidação
                
                # Forçar recarregamento dos dados do Supabase
                print(f"🔄 Forçando recarregamento dos dados do Supabase...")
                self.avaliacao_model._cache_dados = None  # Limpar cache se existir
                
                sucesso, mensagem = self.enviar_avaliacoes_por_email(email_info['email'])
                if sucesso:
                    st.success(f"📧 Email enviado com sucesso para {email_info['email']}")
                else:
                    st.warning(f"⚠️ Email não foi enviado: {mensagem}")
            except Exception as e:
                st.warning(f"⚠️ Erro ao enviar email: {str(e)}")
            finally:
                # Limpar email pendente
                del st.session_state['email_pendente']
    
    def obter_eixos(self) -> List[Dict[str, any]]:
        """Obtém lista de eixos de avaliação com nome, descrição e observações"""
        return self.usuario_model.obter_eixos()
    
    def obter_nomes_eixos(self) -> List[str]:
        """Obtém lista apenas com os nomes dos eixos de avaliação"""
        return self.usuario_model.obter_nomes_eixos()
    
    def obter_descricao_eixo(self, nome_eixo: str) -> str:
        """Obtém a descrição de um eixo específico"""
        return self.usuario_model.obter_descricao_eixo(nome_eixo)
    
    def obter_observacoes_eixo(self, nome_eixo: str) -> List[str]:
        """Obtém as observações de um eixo específico"""
        return self.usuario_model.obter_observacoes_eixo(nome_eixo)
    
    def obter_turmas(self) -> List[str]:
        """Obtém lista de turmas disponíveis"""
        return self.usuario_model.obter_turmas()

    def obter_times(self, turma: str = None) -> List[str]:
        """Obtém lista de times disponíveis para a turma informada ou atual"""
        return self.usuario_model.obter_times(turma)

    def obter_alunos_por_time(self, time: str, turma: str = None) -> List[str]:
        """Obtém lista de alunos de um time para a turma informada ou atual"""
        return self.usuario_model.obter_alunos_por_time(time, turma)
    
    def carregar_dados_sprints(self) -> Dict:
        """
        Carrega os dados das sprints do arquivo sprint_dates_2025_2a.json
        
        Returns:
            Dicionário com os dados das sprints
        """
        try:
            with open('data/sprint_dates_2025_2a.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar dados das sprints: {e}")
            return {}
    
    def obter_sprint_ativa(self) -> str:
        """
        Determina qual sprint está ativa baseada na data atual
        
        Returns:
            Nome da sprint ativa (ex: "Sprint 1", "Sprint 2", etc.)
        """
        dados_sprints = self.carregar_dados_sprints()
        if not dados_sprints or 'sprints' not in dados_sprints:
            return "Sprint 2"  # Fallback padrão
        
        data_atual = datetime.now().date()
        sprints = dados_sprints['sprints']
        
        # Ordenar sprints por data de início
        sprints_ordenadas = []
        for key, sprint in sprints.items():
            try:
                data_inicio = datetime.strptime(sprint['data_inicio'], '%Y-%m-%d').date()
                data_fim = datetime.strptime(sprint['data_fim'], '%Y-%m-%d').date()
                sprints_ordenadas.append({
                    'key': key,
                    'nome': sprint['nome'],
                    'data_inicio': data_inicio,
                    'data_fim': data_fim
                })
            except ValueError as e:
                st.warning(f"Erro ao processar datas da {sprint['nome']}: {e}")
                continue
        
        # Ordenar por data de início
        sprints_ordenadas.sort(key=lambda x: x['data_inicio'])
        
        # Encontrar a sprint ativa
        return sprint["Sprint 5"]
        '''
        for i, sprint in enumerate(sprints_ordenadas):
            # Se estamos dentro do período da sprint
            if sprint['data_inicio'] <= data_atual <= sprint['data_fim']:
                # Retornar a sprint anterior (se existir)
                if i > 0:
                    return sprints_ordenadas[i - 1]['nome']
                else:
                    return sprint['nome']  # Se for a primeira sprint, retornar ela mesma
            
            # Se a sprint terminou e a próxima começa em até 2 dias
            if data_atual > sprint['data_fim']:
                if i + 1 < len(sprints_ordenadas):
                    proxima_sprint = sprints_ordenadas[i + 1]
                    dias_ate_proxima = (proxima_sprint['data_inicio'] - data_atual).days
                    if 0 <= dias_ate_proxima <= 2:
                        # Retornar a sprint anterior à próxima (que seria a atual)
                        return sprint['nome']
        
        # Se não encontrou nenhuma sprint ativa, retornar a primeira disponível
        if sprints_ordenadas:
            return sprints_ordenadas[0]['nome']
        
        return "Sprint 2"  # Fallback padrão
        '''
    def obter_sprints_disponiveis(self) -> List[str]:
        """
        Obtém lista de sprints disponíveis ordenadas
        
        Returns:
            Lista com nomes das sprints
        """
        dados_sprints = self.carregar_dados_sprints()
        if not dados_sprints or 'sprints' not in dados_sprints:
            return [f"Sprint {i}" for i in range(2, 6)]  # Fallback padrão
        
        sprints = dados_sprints['sprints']
        sprints_ordenadas = []
        
        for key, sprint in sprints.items():
            try:
                data_inicio = datetime.strptime(sprint['data_inicio'], '%Y-%m-%d').date()
                sprints_ordenadas.append({
                    'nome': sprint['nome'],
                    'data_inicio': data_inicio
                })
            except ValueError:
                continue
        
        # Ordenar por data de início
        sprints_ordenadas.sort(key=lambda x: x['data_inicio'])
        
        return [sprint['nome'] for sprint in sprints_ordenadas]

    def configurar_turma_grupo(self, turma: str, grupo: str):
        """
        Configura a turma e grupo para o usuário atual
        
        Args:
            turma: Nome da turma (ex: T13)
            grupo: Nome do grupo (ex: Grupo 1)
        """
        # Verificar se o usuário está autenticado antes de configurar
        if not st.session_state.get('user_authenticated', False):
            return
        
        # Configurar turma no modelo de usuário
        self.usuario_model.set_turma(turma)
        
        # Configurar sessão com turma e grupo
        st.session_state.turma_atual = turma
        st.session_state.time_atual = grupo
        
        # Se já temos o nome do usuário logado, usar ele
        if hasattr(st.session_state, 'user_name') and st.session_state.user_name:
            st.session_state.aluno_atual = st.session_state.user_name
            # Buscar o ID do usuário usando MatriculaValidator
            dados_usuario = self.matricula_validator.buscar_aluno_por_email(st.session_state.get('user_email', ''))
            if dados_usuario:
                st.session_state.aluno_id_atual = dados_usuario['id']
            else:
                # Fallback para o método antigo
                st.session_state.aluno_id_atual = self.usuario_model.obter_id_aluno(st.session_state.user_name)
            st.session_state.logado = True
        else:
            # Buscar informações do usuário no grupo (fallback)
            try:
                # Obter alunos do grupo para configurar o usuário atual usando MatriculaValidator
                alunos_grupo = self.matricula_validator.obter_alunos_por_grupo(turma, grupo)
                
                if alunos_grupo:
                    # Configurar o primeiro aluno como usuário atual
                    primeiro_aluno = alunos_grupo[0]
                    st.session_state.aluno_atual = primeiro_aluno.get('nome', '')
                    st.session_state.aluno_id_atual = primeiro_aluno.get('id', 0)
                    st.session_state.logado = True
                    
            except Exception as e:
                st.error(f"Erro ao configurar turma/grupo: {str(e)}")
                st.session_state.logado = False
        
        # Inicializar avaliações temporárias
        if 'avaliacoes_temp' not in st.session_state:
            st.session_state.avaliacoes_temp = {}
        
        # Configurar sprint ativa automaticamente baseada na data atual
        if 'sprint_atual' not in st.session_state:
            st.session_state.sprint_atual = self.obter_sprint_ativa()
