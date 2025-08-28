import streamlit as st
from src.utils.user_storage import UserStorage
from src.utils.matricula_validator import MatriculaValidator
import json

def cadastro_view():
    """Tela de cadastro de novos usuários com validação de matrícula"""
    
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
    st.info("🔐 Cadastre-se usando seu email institucional @sou.inteli.edu.br")
    
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
    if email and email.endswith("@sou.inteli.edu.br"):
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
            
            # Validar se todos os campos obrigatórios foram preenchidos
            if not all([email, password, password_confirm]):
                st.error("❌ Preencha todos os campos obrigatórios!")
                return False
            
            # Validar formato do email
            if not email.endswith("@sou.inteli.edu.br"):
                st.error("❌ Use apenas email institucional @sou.inteli.edu.br")
                return False
            
            # Validar tamanho da senha (6-8 caracteres)
            if len(password) < 6 or len(password) > 8:
                st.error("❌ Senha deve ter entre 6 e 8 caracteres")
                return False
            
            # Validar se as senhas coincidem
            if password != password_confirm:
                st.error("❌ As senhas não coincidem")
                return False
            
            # Verificar se o email é válido na matrícula antes de processar
            if not email_valido or not dados_matricula:
                st.error("❌ Email não validado na matrícula oficial. Verifique se o email está correto.")
                return False
            
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
                st.success("🎉 **Cadastro realizado com sucesso!**")
                st.info(f"**Bem-vindo(a), {nome_final}!** Sua conta foi criada e está pronta para uso.")
                st.balloons()
                
                # Limpar formulário
                st.session_state["show_cadastro"] = False
                
                return True
            else:
                st.error(f"❌ {message}")
                return False
    
    # Após o formulário, mostrar botão para ir ao login se o cadastro foi bem-sucedido
    if st.session_state.get("show_cadastro") == False:
        st.success("✅ Cadastro concluído! Redirecionando...")
        if st.button("🔐 Ir para o Login", type="primary", use_container_width=True):
            st.rerun()
    
    return False
