import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

load_dotenv()
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "avaliacaopares_2026_1a")
# Configurações do Supabase
PERIODO_ATUAL = os.getenv("PERIODO_ATUAL", "2026-1A")  # Período acadêmico atual

def get_current_period() -> str:
    """
    Retorna o período atual baseado na variável de ambiente ou fallback.
    
    Returns:
        String com o período atual (ex: "2025-2A", "2025-2B", "2026-1A")
    """
    return os.getenv("PERIODO_ATUAL", "2026-1A")

def get_bucket_for_period(periodo: str = None) -> str:
    """
    Retorna o nome do bucket baseado no período acadêmico.
    Se nenhum período for especificado, usa o período atual.
    
    Args:
        periodo: Período acadêmico (ex: "2025-2A", "2025-2B"). Se None, usa o período atual.
    
    Returns:
        Nome do bucket para o período especificado
        
    Exemplos:
        get_bucket_for_period("2025-2A") -> "inteli_avaliacao_pares_sprint"
        get_bucket_for_period("2026-1A") -> "avaliacaopares_2026_1a"
        get_bucket_for_period() -> bucket do período atual (PERIODO_ATUAL)
    """
    if periodo is None:
        periodo = PERIODO_ATUAL
    
    if periodo == "2026-1A":
        return "avaliacaopares_2026_1a"
    elif periodo == "2025-2B":
        return "inteli_avalpares_2025_2B"
    else:
        # Para 2025-2A e anteriores, usar o bucket padrão
        return "inteli_avaliacao_pares_sprint"

def get_supabase_client():
    """Cria e retorna cliente Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(f"Configuração Supabase incompleta! URL: {bool(SUPABASE_URL)}, KEY: {bool(SUPABASE_KEY)}")
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"ERRO ao criar cliente Supabase: {e}")
        print(f"URL: {SUPABASE_URL}")
        raise e

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
    import sys
    supabase = get_supabase_client()
    bucket = bucket_name or BUCKET_NAME
    
    # Tentar imprimir sem emojis se possível
    try:
        print(f"Fazendo upload de {file_path} para {bucket}/{bucket_path}")
    except UnicodeEncodeError:
        print(f"Upload: {file_path} -> {bucket}")
    
    # Tenta deletar antes (ignora erro se não existir)
    try:
        supabase.storage.from_(bucket).remove([bucket_path])
    except Exception:
        pass  # Arquivo não existe, tudo bem
    
    # Fazer upload do arquivo
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        result = supabase.storage.from_(bucket).upload(path=bucket_path, file=data)
        print(f"Upload realizado com sucesso")
    except Exception as e:
        print(f"Erro no upload: {e}")
        raise e

def download_json_from_bucket(bucket_path: str, local_path: str, bucket_name: str = None):
    """Faz download de um arquivo do bucket do Supabase para o local."""
    supabase = get_supabase_client()
    bucket = bucket_name or BUCKET_NAME
    res = supabase.storage.from_(bucket).download(bucket_path)
    with open(local_path, "wb") as f:
        f.write(res)

def list_json_files_in_bucket(prefix: str = "", bucket_name: Optional[str] = None, path: str = ""):
    """Lista arquivos JSON no bucket (com paginação), opcionalmente filtrando por prefixo.
    
    Args:
        prefix: Prefixo que o nome do arquivo deve começar (ex: "aval_")
        bucket_name: Nome do bucket a usar; se None, usa BUCKET_NAME
        path: Caminho/pasta dentro do bucket (default raiz)
    """
    supabase = get_supabase_client()
    bucket = bucket_name or BUCKET_NAME

    try:
        all_files = []
        offset = 0
        limit = 1000

        while True:
            files_batch = supabase.storage.from_(bucket).list(
                path=path,
                options={
                    "limit": limit,
                    "offset": offset,
                    "sortBy": {"column": "created_at", "order": "desc"}
                }
            )

            if not files_batch:
                break

            all_files.extend(files_batch)

            if len(files_batch) < limit:
                break

            offset += len(files_batch)

        filtered_files = [
            f["name"] for f in all_files
            if (not prefix or f["name"].startswith(prefix)) and f["name"].endswith(".json")
        ]

        try:
            print(f"📊 Total de arquivos listados em '{bucket}': {len(all_files)}")
            print(f"📊 Arquivos JSON com prefixo '{prefix}': {len(filtered_files)}")
        except Exception:
            pass

        return filtered_files

    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        return []

def list_all_evaluation_files():
    """Lista todos os arquivos de avaliação, contornando limitação de 100 arquivos usando paginação."""
    import requests
    import os
    
    all_files = []
    offset = 0
    limit = 1000  # Limite máximo por página
    
    try:
        # Usar API REST diretamente para contornar limitações
        # A URL correta para listar arquivos do bucket
        url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        print("🔄 Iniciando paginação para listar todos os arquivos...")
        print(f"URL: {url}")
        print(f"Bucket: {BUCKET_NAME}")
        
        while True:
            params = {
                "limit": limit,
                "offset": offset
            }
            
            print(f"📥 Buscando arquivos (offset: {offset}, limit: {limit})...")
            
            response = requests.get(url, headers=headers, params=params)
            
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Erro na requisição: {response.status_code} - {response.text}")
                # Tentar método alternativo usando o cliente Python
                print("🔄 Tentando método alternativo...")
                return _list_files_alternative_method()
            
            files_batch = response.json()
            
            if not files_batch:
                print("✅ Fim dos arquivos alcançado")
                break
            
            print(f"📊 Lote atual: {len(files_batch)} arquivos")
            all_files.extend(files_batch)
            offset += len(files_batch)
            
            # Se retornou menos arquivos que o limite, chegamos ao fim
            if len(files_batch) < limit:
                print("✅ Último lote processado")
                break
        
        print(f"📊 Total de arquivos encontrados: {len(all_files)}")
        
        # Filtrar apenas arquivos de avaliação
        evaluation_files = [
            f["name"] for f in all_files 
            if f["name"].startswith("aval_") and f["name"].endswith(".json")
        ]
        
        print(f"📊 Arquivos de avaliação: {len(evaluation_files)}")
        
        # Verificar turmas encontradas
        turmas = set()
        for arquivo in evaluation_files:
            if '_T' in arquivo:
                try:
                    parts = arquivo.split('_')
                    for part in parts:
                        if part.startswith('T') and len(part) >= 3:
                            turmas.add(part[:3])
                            break
                except:
                    pass
        
        print(f"📊 Turmas encontradas: {sorted(list(turmas))}")
        
        # Verificar T13 especificamente
        arquivos_t13 = [f for f in evaluation_files if 'T13' in f]
        print(f"📊 Arquivos T13: {len(arquivos_t13)}")
        if arquivos_t13:
            print("Arquivos T13 encontrados:")
            for arquivo in arquivos_t13:
                print(f"  - {arquivo}")
        
        return evaluation_files
        
    except Exception as e:
        print(f"❌ Erro ao listar arquivos de avaliação: {e}")
        import traceback
        traceback.print_exc()
        # Tentar método alternativo
        return _list_files_alternative_method()

def _list_files_alternative_method():
    """Método alternativo para listar arquivos usando o cliente Python do Supabase."""
    try:
        print("🔄 Tentando método alternativo com cliente Python...")
        supabase = get_supabase_client()
        
        # Tentar listar com diferentes abordagens
        all_files = []
        
        # Método 1: Listar todos
        files = supabase.storage.from_(BUCKET_NAME).list()
        print(f"📊 Método alternativo retornou: {len(files)} arquivos")
        
        # Filtrar arquivos de avaliação
        evaluation_files = [
            f["name"] for f in files 
            if f["name"].startswith("aval_") and f["name"].endswith(".json")
        ]
        
        print(f"📊 Arquivos de avaliação (método alternativo): {len(evaluation_files)}")
        
        # Verificar turmas
        turmas = set()
        for arquivo in evaluation_files:
            if '_T' in arquivo:
                try:
                    parts = arquivo.split('_')
                    for part in parts:
                        if part.startswith('T') and len(part) >= 3:
                            turmas.add(part[:3])
                            break
                except:
                    pass
        
        print(f"📊 Turmas encontradas (método alternativo): {sorted(list(turmas))}")
        
        # Verificar T13
        arquivos_t13 = [f for f in evaluation_files if 'T13' in f]
        print(f"📊 Arquivos T13 (método alternativo): {len(arquivos_t13)}")
        if arquivos_t13:
            print("Arquivos T13 encontrados:")
            for arquivo in arquivos_t13:
                print(f"  - {arquivo}")
        
        return evaluation_files
        
    except Exception as e:
        print(f"❌ Erro no método alternativo: {e}")
        return []
