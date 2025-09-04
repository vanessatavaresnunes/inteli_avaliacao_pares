"""
View para a tela de avaliação do aplicativo.
Responsável pela interface de avaliação de pares.
"""

import streamlit as st
from src.controllers.avaliacao_controller import AvaliacaoController


class AvaliacaoView:
    """View responsável pela tela de avaliação"""
    
    def __init__(self, controller: AvaliacaoController):
        self.controller = controller
    
    def renderizar(self):
        """Renderiza a tela de avaliação ou tela de sucesso"""
        if st.session_state.get("avaliacao_salva", False):
            self._renderizar_tela_sucesso()
            return


        st.title("📊 Avaliação de Pares")
        
        # Informações do usuário em linha horizontal compacta
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            st.markdown(f"**👤 Nome:** {st.session_state.aluno_atual}")
        
        with col2:
            st.markdown(f"**🏫 Turma:** {st.session_state.get('turma_atual', 'N/A')}")
        
        with col3:
            st.markdown(f"**👥 Grupo:** {st.session_state.time_atual}")
        
        with col4:
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                self.controller.fazer_logout()
        
        st.markdown("---")
        
        # Seleção de sprint (Sprint 1 desabilitada - já acabou)
        st.selectbox("Selecione a Sprint", [f"Sprint {i}" for i in range(2, 6)], key="sprint_atual")

        # Obter dados do usuário atual
        alunos_time = self.controller.obter_alunos_para_avaliar()
        
        # Instruções
        st.markdown(f"### Avalie seus colegas do grupo {st.session_state.time_atual}")
        st.markdown(f"**Instruções:** Para cada eixo, distribua um total de {len(alunos_time) + 1} pontos entre seus colegas.")

        # Matriz de avaliação
        self._renderizar_matriz_avaliacao(alunos_time)

        # Executar validação para garantir que os dados estejam atualizados
        self.controller.validar_avaliacoes()
        
        # Validação das notas
        self._renderizar_validacao_notas(alunos_time)

        # Botão de salvar
        self._renderizar_botao_salvar()
    
    
    
    def _renderizar_matriz_avaliacao(self, alunos_time):
        """Renderiza a matriz de avaliação"""
        st.markdown("---")
        
        # Mostrar informações dos eixos de forma elegante
        self._renderizar_info_eixos()
        
        st.markdown("### 📊 Matriz de Avaliação")
        
        # Inicializar todos os alunos antes de acessar as notas
        for aluno in alunos_time:
            self.controller.inicializar_avaliacao_aluno(aluno)
        # Calcular pontos restantes por eixo (N+1 - soma atual)
        nomes_eixos = self.controller.obter_nomes_eixos()
        num_avaliados = len(alunos_time)
        num_integrantes_grupo = num_avaliados + 1  # +1 para incluir o avaliador
        config = self.controller.obter_configuracao_notas(num_integrantes_grupo)
        pontos_totais = num_integrantes_grupo
        # Soma das notas já distribuídas para cada eixo
        soma_por_eixo = [0 for _ in nomes_eixos]
        for aluno in alunos_time:
            aluno_id = aluno['id']
            notas = st.session_state.avaliacoes_temp[aluno_id]['notas']
            for i, n in enumerate(notas):
                soma_por_eixo[i] += n

        # Avaliações para cada aluno
        for aluno in alunos_time:
            self.controller.inicializar_avaliacao_aluno(aluno)
            aluno_id = aluno['id']
            aluno_nome = aluno['nome']

            # Card para cada aluno
            with st.container(border=True):
                st.markdown(f"##### 👤 {aluno_nome}")
                cols = st.columns(len(nomes_eixos))
                for i, nome_eixo in enumerate(nomes_eixos):
                    with cols[i]:
                        with st.container():
                            st.markdown(f"**{nome_eixo}**", unsafe_allow_html=True)
                            # Mostrar pontos restantes para este eixo
                            pontos_restantes = pontos_totais - soma_por_eixo[i]
                            st.markdown(f"<span style='font-size:11px;color:#888'>Restam <b>{pontos_restantes}</b> ponto(s) para distribuir neste eixo</span>", unsafe_allow_html=True)
                            # Campo de nota
                            st.number_input(
                                "Nota",
                                min_value=config['nota_minima'],
                                max_value=config['nota_maxima'],
                                value=st.session_state.avaliacoes_temp[aluno_id]['notas'][i],
                                key=f"nota_{aluno_id}_{i}",
                                on_change=self.controller.atualizar_nota,
                                args=(aluno_id, i)
                            )
                            # Campo de feedback específico para este eixo
                            st.text_area(
                                "Feedback",
                                value=st.session_state.avaliacoes_temp[aluno_id]['feedbacks'][i],
                                key=f"feedback_{aluno_id}_{i}",
                                height=68,
                                placeholder=f"Comentários sobre {nome_eixo.lower()}...",
                                on_change=self.controller.atualizar_feedback,
                                args=(aluno_id, i)
                            )

    
    def _renderizar_info_eixos(self):
        """Renderiza informações dos eixos de forma elegante"""
        st.markdown("### 📋 Eixos de Avaliação")
        
        nomes_eixos = self.controller.obter_nomes_eixos()
        
        # Criar tabs para cada eixo
        tabs = st.tabs(nomes_eixos)
        
        for i, (tab, nome_eixo) in enumerate(zip(tabs, nomes_eixos)):
            with tab:
                descricao = self.controller.obter_descricao_eixo(nome_eixo)
                observacoes = self.controller.obter_observacoes_eixo(nome_eixo)
                
                st.markdown(f"**Descrição:** {descricao}")
                st.markdown("**O que observar:**")
                
                for obs in observacoes:
                    st.markdown(f"• {obs}")
    
    def _renderizar_validacao_notas(self, alunos_time):
        """Renderiza a seção de validação das notas"""
        st.markdown("### ✅ Validação das Notas")

        # Display messages from session_state
        st.markdown("**Soma das Notas por Eixo:**")
        for eixo, details in st.session_state.validation_messages['soma_notas']['details'].items():
            soma_atual = details.get('soma_atual', 0)
            soma_esperada = details.get('soma_esperada', 0)
            msg = f"{eixo}: {soma_atual}/{soma_esperada} pontos"
            if soma_atual != soma_esperada:
                st.error(msg)
            else:
                st.success(msg)

        st.markdown("**Preenchimento dos Feedbacks:**")
        if st.session_state.validation_messages['feedbacks_preenchidos']['is_valid']:
            st.success("Todos os campos de feedback estão preenchidos.")
        else:
            for msg in st.session_state.validation_messages['feedbacks_preenchidos']['messages']:
                st.error(msg)

        st.markdown("**Feedbacks Únicos:**")
        if st.session_state.validation_messages['feedbacks_unicos']['is_valid']:
            st.success("Os feedbacks para um mesmo aluno são únicos.")
        else:
            for msg in st.session_state.validation_messages['feedbacks_unicos']['messages']:
                st.error(msg)

        st.markdown("**Conteúdo dos Feedbacks:**")
        if st.session_state.validation_messages['conteudo_feedbacks']['is_valid']:
            st.success("O conteúdo de todos os feedbacks é válido.")
        else:
            for msg in st.session_state.validation_messages['conteudo_feedbacks']['messages']:
                st.error(msg)
    
    def _renderizar_botao_salvar(self):
        """Renderiza o botão de salvar avaliações"""
        st.markdown("---")

        # Verificar se todas as validações passaram
        validacoes = self.controller.validar_avaliacoes()
        todas_validas = (
            all(validacoes['soma_notas'].values()) and
            validacoes['notas_individuais'] and
            validacoes['feedbacks_preenchidos'] and
            validacoes['feedbacks_unicos'] and
            validacoes['conteudo_feedbacks']
        )

        # Mostrar mensagem se validação falhar
        if not todas_validas:
            st.warning("⚠️ Corrija os erros de validação acima antes de salvar as avaliações.")
        
        # Desabilitar botão se validação falhar
        if st.button("💾 Salvar Avaliações", type="primary", use_container_width=True, disabled=not todas_validas):
            sucesso, mensagem = self.controller.salvar_avaliacoes()
            if sucesso:
                st.session_state.avaliacao_salva = True
                st.session_state.mensagem_sucesso = mensagem
                # Buscar apenas as avaliações feitas pelo usuário no último envio (maior timestamp)
                from src.models.avaliacao import AvaliacaoModel
                model = AvaliacaoModel()
                df = model.carregar_dados()
                id_avaliador = st.session_state.get('aluno_id_atual')
                df_user = df[df['id_avaliador'] == id_avaliador]
                if not df_user.empty:
                    ultimo_timestamp = df_user['timestamp'].max()
                    avaliacoes_ultima = df_user[df_user['timestamp'] == ultimo_timestamp].to_dict(orient='records')
                else:
                    avaliacoes_ultima = []
                st.session_state.avaliacoes_ultima = avaliacoes_ultima
                st.rerun()
            else:
                st.error(mensagem)
        


    def _obter_avaliacoes_feitas(self):
        """Obtém as avaliações feitas pelo usuário atual em formato estruturado para exibição."""
        avaliacoes = []
        nomes_eixos = self.controller.obter_nomes_eixos()
        alunos = self.controller.obter_alunos_para_avaliar()
        avaliacoes_temp = st.session_state.get('avaliacoes_temp', {})
        for aluno in alunos:
            aluno_id = aluno['id']
            aluno_nome = aluno['nome']
            if aluno_id in avaliacoes_temp:
                notas = avaliacoes_temp[aluno_id]['notas']
                feedbacks = avaliacoes_temp[aluno_id]['feedbacks']
                avaliacoes.append({
                    'aluno_nome': aluno_nome,
                    'notas': notas,
                    'feedbacks': feedbacks
                })
        return {'nomes_eixos': nomes_eixos, 'avaliacoes': avaliacoes}

    def _renderizar_tela_sucesso(self):
        """Renderiza a tela de sucesso após salvar avaliações."""
        # Processar emails pendentes em background
        self.controller.processar_emails_pendentes()
        
        st.title("✅ Avaliações salvas com sucesso!")
        
        # Obter dados do usuário com validações
        id_avaliador = st.session_state.get('aluno_id_atual')
        turma_atual = st.session_state.get('turma_atual')
        user_name = st.session_state.get('user_name')
        aluno_atual = st.session_state.get('aluno_atual')
        
        # Fallback para nome do avaliador - priorizar dados da sessão
        if user_name:
            nome_avaliador = user_name
        elif aluno_atual:
            nome_avaliador = aluno_atual
        elif id_avaliador and turma_atual:
            nome_avaliador = self.controller.usuario_model.obter_nome_aluno(id_avaliador, turma=turma_atual)
        else:
            nome_avaliador = "Usuário"
        
        # Garantir que temos um nome válido
        if not nome_avaliador or nome_avaliador == "None":
            nome_avaliador = "Usuário"
        
        st.markdown(f"**{nome_avaliador}**, suas avaliações foram registradas. Veja abaixo o resumo das avaliações realizadas:")
        
        # Obter avaliações temporárias salvas
        avaliacoes_temp = st.session_state.get('avaliacoes_temp_salvas', st.session_state.get('avaliacoes_temp', {}))
        nomes_eixos = self.controller.obter_nomes_eixos()
        
        if not avaliacoes_temp:
            st.info("Nenhuma avaliação encontrada para exibir.")
            return
        
        # Obter lista de alunos do grupo para mapear IDs para nomes
        alunos_grupo = self.controller.obter_alunos_para_avaliar()
        
        # Verificar se os dados estão sendo carregados corretamente
        if not alunos_grupo:
            st.error("❌ Erro: Nenhum aluno encontrado no grupo!")
            st.info("Tentando carregar dados diretamente do modelo...")
            
            # Tentar carregar dados diretamente do modelo
            if turma_atual and st.session_state.get('time_atual'):
                try:
                    alunos_grupo = self.controller.usuario_model.obter_alunos_por_time(
                        st.session_state.get('time_atual'), 
                        turma_atual
                    )
                    st.success(f"✅ Carregados {len(alunos_grupo)} alunos do modelo")
                except Exception as e:
                    st.error(f"❌ Erro ao carregar do modelo: {e}")
                    alunos_grupo = []
        
        # Se ainda não temos alunos, tentar obter todos os alunos da turma
        if not alunos_grupo and turma_atual:
            try:
                # Obter todos os alunos da turma (incluindo todos os grupos)
                todos_alunos_turma = self.controller.usuario_model._carregar_alunos(turma_atual)
                alunos_grupo = []
                for grupo, alunos_grupo_lista in todos_alunos_turma.items():
                    alunos_grupo.extend(alunos_grupo_lista)
                st.info(f"✅ Carregados {len(alunos_grupo)} alunos de todos os grupos da turma {turma_atual}")
            except Exception as e:
                st.error(f"❌ Erro ao carregar todos os alunos da turma: {e}")
                alunos_grupo = []
        
        # Criar mapeamento ID -> Nome
        mapeamento_id_nome = {}
        for aluno in alunos_grupo:
            if 'id' in aluno and 'nome' in aluno:
                mapeamento_id_nome[aluno['id']] = aluno['nome']
        
        # Se ainda não temos mapeamento, tentar usar o MatriculaValidator diretamente
        if not mapeamento_id_nome and turma_atual and st.session_state.get('time_atual'):
            try:
                from src.utils.matricula_validator import MatriculaValidator
                validator = MatriculaValidator()
                todos_alunos_grupo = validator.obter_alunos_por_grupo(turma_atual, st.session_state.get('time_atual'))
                
                for aluno in todos_alunos_grupo:
                    if 'id' in aluno and 'nome' in aluno:
                        mapeamento_id_nome[aluno['id']] = aluno['nome']
                
                st.info(f"✅ Mapeamento criado via MatriculaValidator: {len(mapeamento_id_nome)} alunos")
            except Exception as e:
                st.error(f"❌ Erro no MatriculaValidator: {e}")
        
        # Debug: mostrar mapeamento criado
        '''
        st.sidebar.markdown("### 🔍 Debug - Mapeamento ID-Nome")
        st.sidebar.markdown(f"**Total de alunos:** {len(alunos_grupo)}")
        st.sidebar.markdown(f"**Mapeamento criado:** {len(mapeamento_id_nome)}")
        st.sidebar.markdown(f"**IDs das avaliações:** {list(avaliacoes_temp.keys())}")
        st.sidebar.markdown(f"**Exemplo mapeamento:** {dict(list(mapeamento_id_nome.items())[:3])}")
        '''
        # Renderizar cada avaliação
        for id_avaliado, notas_feedbacks in avaliacoes_temp.items():
            # Obter nome do aluno avaliado usando o mapeamento local
            nome_avaliado = mapeamento_id_nome.get(id_avaliado)
            
            # Se não encontrou no mapeamento local, tentar pelo modelo
            if not nome_avaliado:
                if turma_atual:
                    nome_avaliado = self.controller.usuario_model.obter_nome_aluno(id_avaliado, turma=turma_atual)
                
                # Fallback final
                if not nome_avaliado or nome_avaliado == "None":
                    nome_avaliado = f"Aluno ID {id_avaliado}"
            
            st.markdown(f"#### 👤 {nome_avaliado}")
            
            # Renderizar notas e feedbacks
            for i, nome_eixo in enumerate(nomes_eixos):
                if i < len(notas_feedbacks['notas']) and i < len(notas_feedbacks['feedbacks']):
                    nota = notas_feedbacks['notas'][i]
                    feedback = notas_feedbacks['feedbacks'][i]
                    st.markdown(f"- **{nome_eixo}**: Nota **{nota}** | Feedback: _{feedback}_")
                else:
                    st.warning(f"⚠️ Dados incompletos para o eixo: {nome_eixo}")
            
            st.markdown("---")
    
    def mostrar_mensagem_erro(self, mensagem: str):
        """
        Mostra mensagem de erro na tela
        
        Args:
            mensagem: Mensagem de erro a ser exibida
        """
        st.error(f"❌ {mensagem}")
    
    def mostrar_mensagem_sucesso(self, mensagem: str):
        """
        Mostra mensagem de sucesso na tela
        
        Args:
            mensagem: Mensagem de sucesso a ser exibida
        """
        st.success(f"✅ {mensagem}")
