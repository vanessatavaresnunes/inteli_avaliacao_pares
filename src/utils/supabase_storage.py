def file_exists_in_bucket(bucket_name: str, file_name: str) -> bool:
    """Verifica se um arquivo existe no bucket do Supabase."""
    supabase = get_supabase_client()
    try:
        files = supabase.storage.from_(bucket_name).list()
        return any(f["name"] == file_name for f in files)
    except Exception:
        return False
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "inteli_avaliacao_pares_sprint")

def get_supabase_client():
    """Cria e retorna cliente Supabase"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_json_to_bucket(file_path: str, bucket_path: str):
    """Faz upload de um arquivo local para o bucket do Supabase, deletando antes se já existir."""
    supabase = get_supabase_client()
    # Tenta deletar antes (ignora erro se não existir)
    try:
        supabase.storage.from_(BUCKET_NAME).remove([bucket_path])
    except Exception:
        pass
    with open(file_path, "rb") as f:
        data = f.read()
    supabase.storage.from_(BUCKET_NAME).upload(path=bucket_path, file=data)

def download_json_from_bucket(bucket_path: str, local_path: str):
    """Faz download de um arquivo do bucket do Supabase para o local."""
    supabase = get_supabase_client()
    res = supabase.storage.from_(BUCKET_NAME).download(bucket_path)
    with open(local_path, "wb") as f:
        f.write(res)

def list_json_files_in_bucket(prefix: str = ""):  # Ex: prefix="avaliacoes_"
    """Lista arquivos JSON no bucket que começam com determinado prefixo no nome."""
    supabase = get_supabase_client()
    files = supabase.storage.from_(BUCKET_NAME).list()
    return [f["name"] for f in files if f["name"].startswith(prefix) and f["name"].endswith(".json")]
