"""
Aplicativo principal do Sistema de Avaliação de Pares.
Implementado seguindo o padrão MVC (Model-View-Controller).
"""

import streamlit as st
from src.controllers.avaliacao_controller import AvaliacaoController
from src.views.login_view_new import login_view
from src.views.cadastro_view_new import cadastro_view
from src.views.password_reset_view import password_reset_view
from src.views.avaliacao_view import AvaliacaoView


def configurar_pagina():
    """Configura as configurações da página Streamlit"""
    st.set_page_config(
        page_title="Sistema de Avaliação de Pares",
        page_icon="📊",
        layout="wide"
    )


def main():
    """Função principal do aplicativo"""
    # Configurar página
    configurar_pagina()
    
    # Inicializar controller
    controller = AvaliacaoController()
    controller.inicializar_sessao()
    
    # Verificar se usuário está autenticado
    if not st.session_state.get("user_authenticated", False):
        # Mostrar tela de login
        if st.session_state.get("show_cadastro", False) or st.session_state.get("cadastro_sucesso"):
            cadastro_view()
        elif st.session_state.get("show_password_reset", False) or st.session_state.get("senha_alterada_sucesso"):
            password_reset_view()
        else:
            login_view()
        return
    
    # Usuário autenticado - mostrar tela de avaliação
    
    # Configurar turma e grupo para o controller
    turma_atual = st.session_state.get("user_turma")
    grupo_atual = st.session_state.get("user_grupo")
    
    if turma_atual and grupo_atual:
        # Configurar controller com a turma e grupo do usuário
        controller.configurar_turma_grupo(turma_atual, grupo_atual)
        
        # Sincronizar variáveis de sessão para compatibilidade
        st.session_state.turma_atual = turma_atual
        st.session_state.time_atual = grupo_atual
        
        # Mostrar tela de avaliação
        avaliacao_view = AvaliacaoView(controller)
        avaliacao_view.renderizar()
    else:
        st.error("❌ Informações de turma/grupo não encontradas. Entre em contato com o administrador.")
        if st.button("🔄 Recarregar"):
            st.rerun()


if __name__ == "__main__":
    main()
