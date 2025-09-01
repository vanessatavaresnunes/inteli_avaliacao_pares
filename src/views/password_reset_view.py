import streamlit as st
from src.utils.user_storage import UserStorage

def password_reset_view():
    """Tela para redefinir senha"""
    
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
                st.success(f"✅ {message}")
                st.balloons()
                
                # Limpar formulário
                st.session_state["show_password_reset"] = False
                
                return True
            else:
                st.error(f"❌ {message}")
                return False
    
    # Mensagem informativa sobre esquecimento de senha
    st.markdown("---")
    st.info("💡 **Esqueceu sua senha?** Entre em contato com o Professor Orientador para redefinir seu acesso ao sistema.")
    
    return False
