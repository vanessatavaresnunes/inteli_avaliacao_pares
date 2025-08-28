import streamlit as st
from src.utils.user_storage import UserStorage
from src.utils.matricula_validator import MatriculaValidator

def login_view():
    """Tela de login principal"""
    
    # Inicializar storage de usuários e validador
    user_storage = UserStorage()
    matricula_validator = MatriculaValidator()
    
    st.title("🔐 Login - Sistema de Avaliação de Pares")
    st.markdown("---")
    
    # Container principal
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Acesso ao Sistema")
            st.info("Use seu email institucional @sou.inteli.edu.br")
            
            # Formulário de login
            with st.form("login_form"):
                email = st.text_input(
                    "📧 Email Institucional",
                    placeholder="seu.nome@sou.inteli.edu.br",
                    help="Digite seu email completo do Inteli"
                )
                
                password = st.text_input(
                    "🔒 Senha",
                    type="password",
                    placeholder="Digite sua senha",
                    help="Digite a senha cadastrada"
                )
                
                submitted = st.form_submit_button("🚀 Entrar", use_container_width=True)
                
                if submitted:
                    if not email or not password:
                        st.error("❌ Preencha todos os campos!")
                        return False
                    
                    if not email.endswith("@sou.inteli.edu.br"):
                        st.error("❌ Use apenas email institucional @sou.inteli.edu.br!")
                        return False
                    
                    # Tentar autenticar usuário
                    success, result = user_storage.authenticate_user(email, password)
                    
                    if success:
                        user_info = result
                        st.success(f"✅ Bem-vindo, {user_info['name']}!")  # Novo campo: name
                        
                        # Buscar informações completas do usuário incluindo grupo
                        dados_completos = matricula_validator.buscar_aluno_por_email(email)
                        
                        # Armazenar informações na sessão
                        st.session_state["user_email"] = email
                        st.session_state["user_name"] = user_info['name']  # Novo campo: name
                        st.session_state["user_turma"] = user_info['turma']
                        st.session_state["user_grupo"] = dados_completos['grupo'] if dados_completos else "Grupo não encontrado"
                        st.session_state["user_authenticated"] = True
                        
                        # Redirecionar para a avaliação
                        st.rerun()
                        return True
                    else:
                        st.error(f"❌ {result}")
                        return False
            
            st.markdown("---")
            
            # Botões de ação
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("📝 Novo Cadastro", use_container_width=True, type="secondary"):
                    st.session_state["show_cadastro"] = True
                    st.rerun()
            
            with col_btn2:
                if st.button("🔑 Esqueci a Senha", use_container_width=True, type="secondary"):
                    st.session_state["show_password_reset"] = True
                    st.rerun()
    
    return False
