
import streamlit as st
import json
import bcrypt
from src.utils.supabase_storage import upload_json_to_bucket, file_exists_in_bucket

def cadastro_usuario():

    st.title("Cadastro de Novo Usuário")
    from src.utils.email_validator import get_allowed_domains_text
    st.info(f"Cadastre-se usando seu email institucional {get_allowed_domains_text()}")
    email = st.text_input(f"Email ({get_allowed_domains_text()})")
    username = st.text_input("Nome de usuário")
    senha = st.text_input("Senha", type="password")
    senha_confirma = st.text_input("Confirme a senha", type="password")
    bucket = "usuarios_inteli"
    if st.button("Cadastrar"):
        if not email or not username or not senha or not senha_confirma:
            st.error("Preencha todos os campos.")
            return
        from src.utils.email_validator import is_valid_inteli_email, get_allowed_domains_text
        if not is_valid_inteli_email(email):
            st.error(f"Use apenas email institucional {get_allowed_domains_text()}.")
            return
        nome_arquivo = email.split("@")[0] + ".json"
        if file_exists_in_bucket(bucket, nome_arquivo):
            st.warning("Usuário já cadastrado para este email.")
            return
        if senha != senha_confirma:
            st.error("As senhas não coincidem.")
            return
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        dados = {
            "email": email,
            "username": username,
            "senha_hash": senha_hash
        }
        upload_json_to_bucket(bucket, nome_arquivo, dados)
        st.success("Usuário cadastrado com sucesso! Faça login para continuar.")

if __name__ == "__main__":
    cadastro_usuario()
