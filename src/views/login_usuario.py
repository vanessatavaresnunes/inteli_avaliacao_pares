import streamlit as st
import bcrypt
import json
from src.utils.supabase_storage import file_exists_in_bucket, download_json_from_bucket
import tempfile

def login_usuario():
    st.title("Login do Usuário")
    email = st.text_input("Email (@sou.inteli.edu.br)")
    senha = st.text_input("Senha", type="password")
    bucket = "usuarios_inteli"
    if st.button("Entrar"):
        if not email or not senha:
            st.error("Preencha todos os campos.")
            return False
        if not email.endswith("@sou.inteli.edu.br"):
            st.error("Use apenas email institucional @sou.inteli.edu.br.")
            return False
        nome_arquivo = email.split("@")[0] + ".json"
        if not file_exists_in_bucket(bucket, nome_arquivo):
            st.error("Usuário não cadastrado. Cadastre-se primeiro.")
            if st.button("Quero me cadastrar", key="cadastro_login"):
                from src.views.cadastro_usuario import cadastro_usuario
                cadastro_usuario()
            return False
        # Baixar o arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            download_json_from_bucket(nome_arquivo, tmp.name)
            with open(tmp.name, "r", encoding="utf-8") as f:
                dados = json.load(f)
        senha_hash = dados.get("senha_hash", "")
        if bcrypt.checkpw(senha.encode(), senha_hash.encode()):
            st.success(f"Bem-vindo, {dados.get('username', email)}!")
            st.session_state["user_email"] = email
            st.session_state["user_name"] = dados.get("username", "")
            return True
        else:
            st.error("Senha incorreta.")
            return False
    # Botão extra para cadastro direto
    st.markdown("---")
    if st.button("Não tenho cadastro. Quero criar um agora!", key="cadastro_abaixo"):
        from src.views.cadastro_usuario import cadastro_usuario
        cadastro_usuario()
    return False

# Exemplo de uso:
if __name__ == "__main__":
    login_usuario()
