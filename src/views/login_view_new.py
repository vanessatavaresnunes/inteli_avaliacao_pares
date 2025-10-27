import streamlit as st
import os
from dotenv import load_dotenv
from src.utils.user_storage import UserStorage
from src.utils.matricula_validator import MatriculaValidator

# Carregar variáveis de ambiente
load_dotenv()

def login_view():
    """Tela de login principal"""
    
    # Determinar período atual
    periodo_atual = os.getenv("PERIODO_ATUAL", "2025-2A")
    
    # Inicializar storage de usuários e validador
    user_storage = UserStorage()
    matricula_validator = MatriculaValidator(periodo=periodo_atual)
    
    st.title("🔐 Login - Sistema de Avaliação de Pares")
    st.markdown("---")
    
    # Container principal
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Acesso ao Sistema")
            from src.utils.email_validator import get_allowed_domains_text
            st.info(f"Use seu email institucional {get_allowed_domains_text()}")
            
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
                    
                    from src.utils.email_validator import is_valid_inteli_email, get_allowed_domains_text
                    if not is_valid_inteli_email(email):
                        st.error(f"❌ Use apenas email institucional {get_allowed_domains_text()}!")
                        return False
                    
                    # Tentar autenticar usuário
                    success, result = user_storage.authenticate_user(email, password)
                    
                    if success:
                        user_info = result
                        st.success(f"✅ Bem-vindo, {user_info['name']}!")  # Novo campo: name
                        
                        # Buscar informações completas do usuário incluindo grupo
                        dados_completos = matricula_validator.buscar_aluno_por_email(email)
                        
                        # Armazenar informações na sessão
                        st.session_state["user_email"] = email.lower()  # Normalizar para minúsculas
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
                if st.button("📝 Criar Nova Conta", use_container_width=True, type="secondary"):
                    st.session_state["show_cadastro"] = True
                    st.rerun()
            
            with col_btn2:
                if st.button("🔑 Alterar Senha", use_container_width=True, type="secondary"):
                    st.session_state["show_password_reset"] = True
                    st.rerun()
    
    return False
