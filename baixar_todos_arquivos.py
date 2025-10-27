#!/usr/bin/env python3
"""
Script para baixar TODOS os arquivos JSON do Supabase para a pasta dados
Usa paginação para garantir que todos os arquivos sejam baixados (mais de 1000)
"""

from src.utils.supabase_storage import get_supabase_client, download_json_from_bucket
import os
from pathlib import Path

def main():
    print("📥 DOWNLOAD DE TODOS OS ARQUIVOS JSON DO SUPABASE")
    print("="*100)
    
    # Criar pasta dados se não existir
    pasta_dados = Path("dados")
    pasta_dados.mkdir(parents=True, exist_ok=True)
    print(f"✅ Pasta 'dados' pronta\n")
    
    # Conectar ao Supabase
    print("🔗 Conectando ao Supabase...")
    supabase = get_supabase_client()
    
    # Listar TODOS os arquivos com paginação
    print("📋 Listando todos os arquivos com paginação...\n")
    
    todos_arquivos = []
    offset = 0
    limit = 1000
    pagina = 1
    
    while True:
        print(f"   Página {pagina}: Buscando arquivos {offset} a {offset + limit}...")
        
        try:
            from src.utils.supabase_storage import get_bucket_for_period
            bucket_name = get_bucket_for_period()  # Usa 2025-2A como padrão
            arquivos = supabase.storage.from_(bucket_name).list(
                path="",
                options={
                    "limit": limit,
                    "offset": offset,
                    "sortBy": {"column": "created_at", "order": "desc"}
                }
            )
            
            if not arquivos:
                print(f"   ✅ Fim dos arquivos alcançado")
                break
            
            print(f"   ✅ Encontrados: {len(arquivos)} arquivos")
            todos_arquivos.extend(arquivos)
            
            if len(arquivos) < limit:
                print(f"   ✅ Último lote processado")
                break
            
            offset += len(arquivos)
            pagina += 1
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            break
    
    print(f"\n📊 Total de arquivos encontrados: {len(todos_arquivos)}")
    
    # Filtrar apenas arquivos JSON
    arquivos_json = [f for f in todos_arquivos if f["name"].endswith(".json")]
    print(f"📊 Arquivos JSON: {len(arquivos_json)}")
    
    # Separar por tipo
    arquivos_aval = [f for f in arquivos_json if f["name"].startswith("aval_")]
    arquivos_outros = [f for f in arquivos_json if not f["name"].startswith("aval_")]
    
    print(f"   - Arquivos de avaliação: {len(arquivos_aval)}")
    print(f"   - Outros arquivos JSON: {len(arquivos_outros)}")
    
    # Analisar por turma
    turmas = {}
    for arq in arquivos_aval:
        nome = arq["name"]
        if "_T09_" in nome:
            turma = "T09"
        elif "_T13_" in nome:
            turma = "T13"
        elif "_Teste_" in nome:
            turma = "Teste"
        else:
            turma = "Outra"
        
        if turma not in turmas:
            turmas[turma] = 0
        turmas[turma] += 1
    
    print(f"\n📊 Distribuição por turma:")
    for turma, count in sorted(turmas.items()):
        print(f"   {turma}: {count} arquivos")
    
    # Baixar todos os arquivos JSON
    print(f"\n{'='*100}")
    print(f"📥 INICIANDO DOWNLOAD DE {len(arquivos_json)} ARQUIVOS")
    print(f"{'='*100}\n")
    
    sucesso = 0
    erros = 0
    
    for i, arq in enumerate(arquivos_json, 1):
        nome_arquivo = arq["name"]
        caminho_local = pasta_dados / nome_arquivo
        
        try:
            # Baixar arquivo
            download_json_from_bucket(nome_arquivo, str(caminho_local))
            sucesso += 1
            
            # Mostrar progresso a cada 10 arquivos
            if i % 10 == 0:
                print(f"   [{i}/{len(arquivos_json)}] ✅ {nome_arquivo}")
            
        except Exception as e:
            erros += 1
            print(f"   [{i}/{len(arquivos_json)}] ❌ Erro ao baixar {nome_arquivo}: {e}")
    
    # Resumo final
    print(f"\n{'='*100}")
    print(f"📊 RESUMO DO DOWNLOAD")
    print(f"{'='*100}")
    print(f"✅ Arquivos baixados com sucesso: {sucesso}")
    print(f"❌ Arquivos com erro: {erros}")
    print(f"📁 Pasta de destino: {pasta_dados.absolute()}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()


