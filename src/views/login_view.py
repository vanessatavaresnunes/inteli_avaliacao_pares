"""
View para a tela de login do aplicativo.
Responsável pela interface de autenticação.
"""

import streamlit as st
from src.controllers.avaliacao_controller import AvaliacaoController


class LoginView:
    """View responsável pela tela de login"""
    
    def __init__(self, controller: AvaliacaoController):
        self.controller = controller
    
    def renderizar(self):
        """Renderiza a tela de login"""
        st.title("🎓 Sistema de Avaliação de Pares")
        st.markdown("---")

        # Layout centralizado
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 🔐 Login")

            # Seleção da turma
            turmas = self.controller.obter_turmas()
            turma_selecionada = st.selectbox(
                "Selecione sua turma:",
                turmas,
                key="login_turma"
            )

            # Seleção do time (de acordo com a turma)
            times = self.controller.obter_times(turma=turma_selecionada)
            time_selecionado = st.selectbox(
                "Selecione seu time:",
                times,
                key="login_time"
            )

            # Lista de alunos do time selecionado e turma
            alunos_do_time = self.controller.obter_alunos_por_time(time_selecionado, turma=turma_selecionada)
            nomes_alunos = sorted([aluno['nome'] for aluno in alunos_do_time])

            # Seleção do aluno
            aluno_selecionado = st.selectbox(
                "Selecione seu nome:",
                nomes_alunos,
                key="login_aluno"
            )

            # Campo de senha
            senha = st.text_input(
                "Senha:",
                type="password",
                key="login_senha"
            )

            # Botão de login
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🚀 Entrar no Sistema", type="primary", use_container_width=True):
                    if self.controller.fazer_login(time_selecionado, aluno_selecionado, senha, turma=turma_selecionada):
                        st.success(f"✅ Bem-vindo(a), {aluno_selecionado}!")
                        st.rerun()
                    else:
                        st.error("❌ Erro no login. Verifique suas credenciais.")
    
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
