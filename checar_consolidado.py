
import pandas as pd
import json
import tempfile
import os
from src.utils.supabase_storage import download_json_from_bucket

def carregar_dados_consolidados():
    """Carrega dados do arquivo consolidado do Supabase."""
    print("Baixando 'avaliacoescompletas_consolidadas.json' do Supabase...")
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as tmp:
            download_json_from_bucket('avaliacoescompletas_consolidadas.json', tmp.name)
            tmp.seek(0)
            conteudo = tmp.read().decode("utf-8").strip()
            if not conteudo:
                print("Arquivo está vazio.")
                return pd.DataFrame()
            
            print("Arquivo baixado. Processando linhas...")
            linhas = [json.loads(linha) for linha in conteudo.splitlines() if linha.strip()]
            return pd.DataFrame(linhas)
    except Exception as e:
        print(f"ERRO: Falha ao baixar ou processar o arquivo: {e}")
        return pd.DataFrame()
    finally:
        try:
            os.unlink(tmp.name)
        except:
            pass

# --- Início do Script de Checagem ---
print("Iniciando checagem do arquivo consolidado no Supabase...")
df = carregar_dados_consolidados()

if df.empty:
    print("\nAnálise interrompida pois não foi possível carregar os dados.")
    exit()

print("\n--- RELATÓRIO DO ARQUIVO CONSOLIDADO ---")

# 1. Contagem total
num_avaliacoes = len(df)
print(f"Total de Avaliações no Arquivo: {num_avaliacoes}")

# 2. Checagem de colunas essenciais
essential_cols = ['timestamp', 'turma']
if not all(col in df.columns for col in essential_cols):
    print(f"ERRO: O arquivo não contém as colunas essenciais: {essential_cols}")
    exit()

# 3. Análise de Datas
df['timestamp_numeric'] = pd.to_numeric(df['timestamp'], errors='coerce')

# Tenta converter para datetime. 'coerce' transformará erros (datas fora do limite) em NaT (Not a Time)
df['data_avaliacao'] = pd.to_datetime(df['timestamp_numeric'], unit='s', errors='coerce')

# Checar se houve erros de conversão
linhas_com_erro = df[df['data_avaliacao'].isnull()]
erros_de_data = len(linhas_com_erro)

if erros_de_data > 0:
    print(f"\nAVISO: {erros_de_data} avaliações têm um timestamp inválido ou grande demais (provavelmente em milissegundos).")
    print("As seguintes linhas estão corrompidas e foram ignoradas na análise de datas:")
    print(linhas_com_erro[['id_avaliador', 'nome_avaliador', 'turma', 'time', 'sprint', 'timestamp']])
    
    # Remove as linhas com data inválida para as próximas análises
    df.dropna(subset=['data_avaliacao'], inplace=True)

data_mais_antiga = df['data_avaliacao'].min()
data_mais_recente = df['data_avaliacao'].max()

print(f"Data da Avaliação Mais Antiga: {data_mais_antiga.strftime('%d/%m/%Y %H:%M:%S') if pd.notna(data_mais_antiga) else 'N/A'}")
print(f"Data da Avaliação Mais Recente: {data_mais_recente.strftime('%d/%m/%Y %H:%M:%S') if pd.notna(data_mais_recente) else 'N/A'}")

# 4. Lista de Turmas
turmas_encontradas = sorted(df['turma'].astype(str).unique())
print(f"Turmas Encontradas no Arquivo ({len(turmas_encontradas)}):")
for turma in turmas_encontradas:
    print(f"- {turma}")

print("\n--- Fim do Relatório ---")

