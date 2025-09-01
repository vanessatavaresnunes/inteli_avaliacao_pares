import streamlit as st
from src.utils.user_storage import UserStorage

def password_reset_view():
    """Tela para redefinir senha"""
    
    # Verificar se há sucesso de alteração de senha para mostrar
    if st.session_state.get("senha_alterada_sucesso"):
        dados_sucesso = st.session_state["senha_alterada_sucesso"]
        
        # Container principal para a mensagem de sucesso
        success_container = st.container()
        
        with success_container:
            st.title("✅ Senha Alterada com Sucesso!")
            st.markdown("---")
            
            # Mostrar mensagem de sucesso
            st.success("🔑 **Senha alterada com sucesso!**")
            st.balloons()
            
            # Container com informações detalhadas
            with st.container(border=True):
                st.markdown("### ✅ Alteração Realizada!")
                st.markdown(f"**📧 Email:** {dados_sucesso['email']}")
                st.markdown(f"**👤 Nome:** {dados_sucesso['nome']}")
                st.markdown(f"**🏫 Turma:** {dados_sucesso['turma']}")
                st.markdown("**🔐 Status:** Senha atualizada com sucesso")
                st.markdown("**⏰ Data/Hora:** " + dados_sucesso['timestamp'])
            
            # Botão para ir ao login
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔐 Ir para o Login", type="primary", use_container_width=True):
                    # Limpar dados de sucesso e voltar ao login
                    del st.session_state["senha_alterada_sucesso"]
                    st.session_state["show_password_reset"] = False
                    st.rerun()
        
        # Mensagem de sucesso exibida com sucesso
        
        return True
    
    # Inicializar storage de usuários
    user_storage = UserStorage()
    
    st.title("🔑 Alterar Senha")
    st.markdown("---")
    
    # Botão para voltar ao login
    if st.button("← Voltar ao Login", type="secondary"):
        st.session_state["show_password_reset"] = False
        st.rerun()
    
    st.markdown("### Alterar sua senha")
    st.info("🔐 Digite seu email institucional, senha atual e nova senha")
    
    # Formulário de redefinição
    with st.form("password_reset_form"):
        email = st.text_input(
            "📧 Email Institucional",
            placeholder="seu.nome@sou.inteli.edu.br",
            help="Digite seu email completo do Inteli"
        )
        
        current_password = st.text_input(
            "🔒 Senha Atual",
            type="password",
            placeholder="Digite sua senha atual",
            help="Digite a senha que você está usando atualmente"
        )
        
        new_password = st.text_input(
            "🔒 Nova Senha",
            type="password",
            placeholder="Digite uma nova senha segura",
            help="Mínimo 6 caracteres"
        )
        
        confirm_password = st.text_input(
            "🔒 Confirme a Nova Senha",
            type="password",
            placeholder="Digite a nova senha novamente",
            help="Confirme sua nova senha"
        )
        
        submitted = st.form_submit_button("🔄 Alterar Senha", use_container_width=True)
        
        if submitted:
            if not all([email, current_password, new_password, confirm_password]):
                st.error("❌ Preencha todos os campos!")
                return False
            
            from src.utils.email_validator import is_valid_inteli_email, get_allowed_domains_text
            if not is_valid_inteli_email(email):
                st.error(f"❌ Use apenas email institucional {get_allowed_domains_text()}!")
                return False
            
            # Verificar se a senha atual está correta
            if not user_storage.authenticate_user(email, current_password):
                st.error("❌ Senha atual incorreta!")
                return False
            
            if new_password != confirm_password:
                st.error("❌ As senhas não coincidem!")
                return False
            
            if len(new_password) < 6:
                st.error("❌ A senha deve ter pelo menos 6 caracteres!")
                return False
            
            # Tentar atualizar senha
            success, message = user_storage.update_password(email, new_password)
            
            if success:
                # Buscar informações do usuário para mostrar na mensagem de sucesso
                user_info = user_storage.get_user_info(email)
                nome_usuario = user_info.get('name', 'Usuário') if user_info else 'Usuário'
                turma_usuario = user_info.get('turma', 'N/A') if user_info else 'N/A'
                
                # Armazenar dados do sucesso na sessão para mostrar fora do formulário
                from datetime import datetime
                timestamp_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
                
                st.session_state["senha_alterada_sucesso"] = {
                    "email": email,
                    "nome": nome_usuario,
                    "turma": turma_usuario,
                    "timestamp": timestamp_atual
                }
                
                # NÃO definir show_password_reset = False aqui, para manter na tela de alteração
                st.rerun()
                return True
            else:
                st.error(f"❌ {message}")
                return False
    
    # Mensagem informativa sobre esquecimento de senha
    st.markdown("---")
    st.info("💡 **Esqueceu sua senha?** Entre em contato com o Professor Orientador para redefinir seu acesso ao sistema.")
    
    return False
