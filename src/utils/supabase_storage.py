import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "inteli_avaliacao_pares_sprint")

def get_supabase_client():
    """Cria e retorna cliente Supabase"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def file_exists_in_bucket(bucket_name: str, file_name: str) -> bool:
    """Verifica se um arquivo existe no bucket do Supabase."""
    supabase = get_supabase_client()
    try:
        files = supabase.storage.from_(bucket_name).list()
        return any(f["name"] == file_name for f in files)
    except Exception:
        return False

def upload_json_to_bucket(file_path: str, bucket_path: str, bucket_name: str = None):
    """Faz upload de um arquivo local para o bucket do Supabase, deletando antes se já existir."""
    supabase = get_supabase_client()
    bucket = bucket_name or BUCKET_NAME
    
    print(f"📤 Fazendo upload de {file_path} para {bucket}/{bucket_path}")
    
    # Tenta deletar antes (ignora erro se não existir)
    try:
        print(f"🗑️ Tentando remover arquivo existente: {bucket_path}")
        supabase.storage.from_(bucket).remove([bucket_path])
        print(f"✅ Arquivo removido com sucesso")
    except Exception as e:
        print(f"ℹ️ Arquivo não existia ou erro ao remover: {e}")
    
    # Fazer upload do arquivo
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        print(f"📤 Enviando {len(data)} bytes para {bucket}/{bucket_path}")
        result = supabase.storage.from_(bucket).upload(path=bucket_path, file=data)
        print(f"✅ Upload realizado com sucesso: {result}")
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        raise e

def download_json_from_bucket(bucket_path: str, local_path: str, bucket_name: str = None):
    """Faz download de um arquivo do bucket do Supabase para o local."""
    supabase = get_supabase_client()
    bucket = bucket_name or BUCKET_NAME
    res = supabase.storage.from_(bucket).download(bucket_path)
    with open(local_path, "wb") as f:
        f.write(res)

def list_json_files_in_bucket(prefix: str = ""):  # Ex: prefix="avaliacoes_"
    """Lista arquivos JSON no bucket que começam com determinado prefixo no nome."""
    supabase = get_supabase_client()
    files = supabase.storage.from_(BUCKET_NAME).list()
    return [f["name"] for f in files if f["name"].startswith(prefix) and f["name"].endswith(".json")]
