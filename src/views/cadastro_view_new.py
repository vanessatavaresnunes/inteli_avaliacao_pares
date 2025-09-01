import streamlit as st
from src.utils.user_storage import UserStorage
from src.utils.matricula_validator import MatriculaValidator
import json

def cadastro_view():
    """Tela de cadastro de novos usuários com validação de matrícula"""
    
    # Verificar se há sucesso de cadastro para mostrar
    if st.session_state.get("cadastro_sucesso"):
        dados_sucesso = st.session_state["cadastro_sucesso"]
        
        # Debug: verificar se os dados estão corretos
        # st.write("Debug - Dados de sucesso:", dados_sucesso)
        
        # Container principal para posicionar a tela
        success_container = st.container()
        
        with success_container:
            st.title("🎉 Cadastro Realizado com Sucesso!")
            st.markdown("---")
            
            # Mostrar mensagem de sucesso
            st.success("🎉 **Cadastro realizado com sucesso!**")
            st.balloons()
            
            # Container com informações detalhadas
            with st.container(border=True):
                st.markdown("### ✅ Conta Criada com Sucesso!")
                st.markdown(f"**👤 Nome:** {dados_sucesso['nome']}")
                st.markdown(f"**📧 Email:** {dados_sucesso['email']}")
                st.markdown(f"**🏫 Turma:** {dados_sucesso['turma']}")
                st.markdown(f"**👥 Grupo:** {dados_sucesso['grupo']}")
                st.markdown("**🔐 Status:** Conta ativa e pronta para uso")
            
            # Botão para ir ao login
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔐 Ir para o Login", type="primary", use_container_width=True):
                    # Limpar dados de sucesso e voltar ao login
                    del st.session_state["cadastro_sucesso"]
                    st.session_state["show_cadastro"] = False
                    st.rerun()
        
        # Mensagem de sucesso exibida com sucesso
        
        return True
    
    # Inicializar storage de usuários e validador
    user_storage = UserStorage()
    matricula_validator = MatriculaValidator()
    
    st.title("📝 Cadastro de Novo Usuário")
    st.markdown("---")
    
    # Botão para voltar ao login
    if st.button("← Voltar ao Login", type="secondary"):
        st.session_state["show_cadastro"] = False
        st.rerun()
    
    st.markdown("### Informações Pessoais")
    from src.utils.email_validator import get_allowed_domains_text
    st.info(f"🔐 Cadastre-se usando seu email institucional {get_allowed_domains_text()}")
    
    # Inicializar variáveis de sessão
    if 'nome_usuario_encontrado' not in st.session_state:
        st.session_state.nome_usuario_encontrado = ""
    
    # Campo de email fora do formulário para permitir atualização em tempo real
    email = st.text_input(
        "📧 Email Institucional",
        placeholder="seu.nome@sou.inteli.edu.br",
        help="Digite seu email completo do Inteli",
        key="email_input_cadastro"
    )
    
    # Buscar nome do usuário quando email for digitado
    from src.utils.email_validator import is_valid_inteli_email
    if email and is_valid_inteli_email(email):
        user_info = user_storage.get_user_info(email)
        if user_info and user_info.get('name'):
            st.session_state.nome_usuario_encontrado = user_info.get('name')
        else:
            st.session_state.nome_usuario_encontrado = ""
            # Mostrar mensagem de erro se email não pertencer à base
            st.error("❌ **Aluno não tem direito de acesso!** Entre em contato com o Professor Orientador para verificar sua matrícula.")
            
            # Botão para voltar ao cadastro quando email não existe na base
            if st.button("← Voltar ao Cadastro", type="secondary", use_container_width=True):
                st.session_state["show_cadastro"] = False
                st.rerun()
    
    # Formulário de cadastro
    with st.form("cadastro_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Campo de nome (editável apenas se não foi encontrado)
            if not st.session_state.nome_usuario_encontrado:
                username = st.text_input(
                    "👤 Nome Completo",
                    placeholder="Seu nome completo",
                    help="Digite seu nome completo (mínimo 3 caracteres)",
                    key="nome_input_cadastro"
                )
            else:
                # Campo de nome desabilitado quando encontrado
                username = st.text_input(
                    "👤 Nome Completo",
                    value=st.session_state.nome_usuario_encontrado,
                    disabled=True,
                    help="Nome encontrado automaticamente - não pode ser alterado",
                    key="nome_input_cadastro_disabled"
                )
                # Importante: definir username mesmo quando o campo está desabilitado
                username = st.session_state.nome_usuario_encontrado
        
        with col2:
            password = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Digite uma senha segura",
                help="Entre 6 e 8 caracteres"
            )
            
            password_confirm = st.text_input(
                "🔒 Confirme a Senha",
                type="password",
                placeholder="Digite a senha novamente",
                help="Confirme sua senha"
            )
        
        # Validação de matrícula
        
        dados_matricula = None
        email_valido = False
        usuario_pre_cadastrado = False
        
        if email:
            # Validar email contra lista oficial
            email_valido, dados_matricula = matricula_validator.validar_email_matricula(email)
            
            if email_valido:
                # Verificar se é usuário pré-cadastrado
                usuario_pre_cadastrado = not dados_matricula.get('passwd', True)  # Novo campo: passwd
                
                # Mostrar informações de turma e grupo em um único label azul
                st.info(f"🏫 Turma: {dados_matricula['turma']} | 👥 Grupo: {dados_matricula['grupo']}")
            else:
                # Não retornar False aqui para permitir que o formulário seja renderizado
                pass
        
        # Validações serão feitas apenas quando o formulário for submetido
        # para evitar problemas com campos de formulário do Streamlit
        
        # Botão de cadastro sempre habilitado para usuários válidos
        if email_valido and usuario_pre_cadastrado:
            button_text = "🔓 Ativar Conta"
            button_help = "Ativar sua conta pré-cadastrada criando uma senha"
            
            submitted = st.form_submit_button(
                button_text,
                use_container_width=True,
                type="primary",
                help=button_help
            )
        elif email_valido and not usuario_pre_cadastrado:
            button_text = "🚀 Criar Conta"
            button_help = "Criar nova conta de usuário"
            
            submitted = st.form_submit_button(
                button_text,
                use_container_width=True,
                type="primary",
                help=button_help
            )
        else:
            # Email não existe na base - mostrar botão desabilitado
            submitted = st.form_submit_button(
                "🚫 Cadastro Bloqueado",
                use_container_width=True,
                type="secondary",
                disabled=True,
                help="Email não validado na matrícula oficial"
            )
        
        if submitted:
            # Validações feitas apenas quando o formulário é submetido
            # (aqui os valores dos campos estão disponíveis)
            
            # Variável para controlar se deve processar o cadastro
            pode_processar = True
            
            # Validar se todos os campos obrigatórios foram preenchidos
            if not all([email, password, password_confirm]):
                st.error("❌ Preencha todos os campos obrigatórios!")
                pode_processar = False
            
            # Validar formato do email
            from src.utils.email_validator import is_valid_inteli_email, get_allowed_domains_text
            if pode_processar and not is_valid_inteli_email(email):
                st.error(f"❌ Use apenas email institucional {get_allowed_domains_text()}")
                pode_processar = False
            
            # Validar tamanho da senha (6-8 caracteres)
            if pode_processar and (len(password) < 6 or len(password) > 8):
                st.error("❌ Senha deve ter entre 6 e 8 caracteres")
                pode_processar = False
            
            # Validar se as senhas coincidem
            if pode_processar and password != password_confirm:
                st.error("❌ As senhas não coincidem")
                pode_processar = False
            
            # Verificar se o email é válido na matrícula antes de processar
            if pode_processar and (not email_valido or not dados_matricula):
                st.error("❌ Email não validado na matrícula oficial. Verifique se o email está correto.")
                pode_processar = False
            
            # Só processar o cadastro se todas as validações passaram
            if pode_processar:
                # Usar dados da matrícula oficial
                turma = dados_matricula['turma']
                grupo = dados_matricula['grupo']
                
                # Usar nome encontrado no usuarios.json se disponível, senão usar o digitado
                nome_final = st.session_state.nome_usuario_encontrado if st.session_state.nome_usuario_encontrado else username
                
                if usuario_pre_cadastrado:
                    # Ativar usuário pré-cadastrado
                    success, message = user_storage.create_user(email, dados_matricula['nome'], password, turma, grupo)  # Novo campo: nome
                else:
                    # Criar novo usuário
                    success, message = user_storage.create_user(email, nome_final, password, turma, grupo)
                
                if success:
                    # Armazenar dados do sucesso na sessão para mostrar fora do formulário
                    st.session_state["cadastro_sucesso"] = {
                        "nome": nome_final,
                        "email": email,
                        "turma": turma,
                        "grupo": grupo
                    }
                    # NÃO definir show_cadastro = False aqui, para manter na tela de cadastro
                    st.rerun()
                    return True
                else:
                    st.error(f"❌ {message}")
                    return False
    
    return False
