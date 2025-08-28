import streamlit as st
from src.utils.user_storage import UserStorage

def password_reset_view():
    """Tela para redefinir senha"""
    
    # Inicializar storage de usuários
    user_storage = UserStorage()
    
    st.title("🔑 Redefinir Senha")
    st.markdown("---")
    
    # Botão para voltar ao login
    if st.button("← Voltar ao Login", type="secondary"):
        st.session_state["show_password_reset"] = False
        st.rerun()
    
    st.markdown("### Redefinir sua senha")
    st.info("🔐 Digite seu email institucional e uma nova senha")
    
    # Formulário de redefinição
    with st.form("password_reset_form"):
        email = st.text_input(
            "📧 Email Institucional",
            placeholder="seu.nome@sou.inteli.edu.br",
            help="Digite seu email completo do Inteli"
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
        
        submitted = st.form_submit_button("🔄 Atualizar Senha", use_container_width=True)
        
        if submitted:
            if not all([email, new_password, confirm_password]):
                st.error("❌ Preencha todos os campos!")
                return False
            
            if not email.endswith("@sou.inteli.edu.br"):
                st.error("❌ Use apenas email institucional @sou.inteli.edu.br!")
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
                
                # Mostrar botão para ir ao login
                if st.button("🔐 Ir para o Login", type="primary"):
                    st.rerun()
                
                return True
            else:
                st.error(f"❌ {message}")
                return False
    
    return False
