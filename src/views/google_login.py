import streamlit as st
from streamlit_oauth import OAuth2Component
import os

# Substitua pelos seus dados do Google Cloud Console
go_client_id = st.secrets["GOOGLE_CLIENT_ID"] if "GOOGLE_CLIENT_ID" in st.secrets else os.getenv("GOOGLE_CLIENT_ID", "")
go_client_secret = st.secrets["GOOGLE_CLIENT_SECRET"] if "GOOGLE_CLIENT_SECRET" in st.secrets else os.getenv("GOOGLE_CLIENT_SECRET", "")

redirect_uri = "http://localhost:8501/"

# Configuração do OAuth2 para Google
google_auth = OAuth2Component(
    client_id=go_client_id,
    client_secret=go_client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    revoke_endpoint="https://oauth2.googleapis.com/revoke",
    redirect_uri=redirect_uri,
    scope=["openid", "email", "profile"],
)

def google_login():
    st.write("## Login com Google (somente @sou.inteli.edu.br)")
    result = google_auth.authorize_button("Login com Google", key="google_login")
    if result and "token" in result:
        userinfo = google_auth.get_user_info(result["token"], user_info_endpoint="https://openidconnect.googleapis.com/v1/userinfo")
        email = userinfo.get("email", "")
        if email.endswith("@sou.inteli.edu.br"):
            st.success(f"Bem-vindo, {userinfo.get('name', email)}!")
            st.session_state["user_email"] = email
            st.session_state["user_name"] = userinfo.get("name", "")
            return True
        else:
            st.error("Apenas emails @sou.inteli.edu.br são permitidos.")
            return False
    return False

# Exemplo de uso:
if __name__ == "__main__":
    google_login()
