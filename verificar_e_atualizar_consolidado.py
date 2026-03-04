#!/usr/bin/env python3
"""
Script para verificar e atualizar o arquivo consolidado de avaliações.
Compara o arquivo consolidado com os arquivos individuais no bucket
e regenera o consolidado se necessário.
"""

import sys
import os
import pandas as pd
from datetime import datetime
from src.models.avaliacao import AvaliacaoModel
from src.utils.supabase_storage import get_bucket_for_period, get_current_period, list_json_files_in_bucket, download_json_from_bucket
import tempfile
import json

def verificar_consolidado(periodo: str = None):
    """
    Verifica o estado do arquivo consolidado e compara com arquivos individuais.
    
    Args:
        periodo: Período acadêmico (ex: "2025-2A", "2025-2B"). Se None, usa o período atual.
    """
    if periodo is None:
        periodo = get_current_period()
    
    print("=" * 80)
    print(f"🔍 VERIFICAÇÃO DO ARQUIVO CONSOLIDADO - {periodo}")
    print("=" * 80)
    print()
    
    bucket_name = get_bucket_for_period(periodo)
    print(f"📦 Bucket: {bucket_name}")
    print()
    
    # 1. Listar todos os arquivos de avaliação no bucket
    print("📋 Listando arquivos de avaliação no bucket...")
    arquivos = list_json_files_in_bucket(prefix="aval_", bucket_name=bucket_name)
    arquivos_avaliacao = [f for f in arquivos if f.startswith('aval_') and f.endswith('.json')]
    
    print(f"✅ Encontrados {len(arquivos_avaliacao)} arquivos de avaliação individuais")
    print()
    
    # 2. Carregar arquivo consolidado atual
    print("📥 Carregando arquivo consolidado atual...")
    df_consolidado = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as tmp:
            download_json_from_bucket('avaliacoescompletas_consolidadas.json', tmp.name, bucket_name=bucket_name)
            tmp.seek(0)
            conteudo = tmp.read().decode("utf-8").strip()
            
            if conteudo:
                linhas = [json.loads(linha) for linha in conteudo.splitlines() if linha.strip()]
                df_consolidado = pd.DataFrame(linhas)
                print(f"✅ Arquivo consolidado carregado: {len(df_consolidado)} registros")
            else:
                print("⚠️ Arquivo consolidado está vazio")
                df_consolidado = pd.DataFrame()
    except Exception as e:
        print(f"⚠️ Erro ao carregar arquivo consolidado: {e}")
        print("   (Isso é normal se o arquivo não existir ainda)")
        df_consolidado = pd.DataFrame()
    finally:
        try:
            os.unlink(tmp.name)
        except:
            pass
    
    print()
    
    # 3. Analisar datas dos arquivos individuais
    print("📅 Analisando datas dos arquivos individuais...")
    datas_arquivos = []
    for arquivo in arquivos_avaliacao:
        # Extrair data do nome do arquivo (formato: aval_T09_Grupo 1_Sprint 2_44_20250903_0936.json)
        try:
            partes = arquivo.split('_')
            if len(partes) >= 5:
                data_str = partes[-2]  # Ex: "20250903"
                hora_str = partes[-1].replace('.json', '')  # Ex: "0936"
                if len(data_str) == 8 and len(hora_str) == 4:
                    ano = int(data_str[:4])
                    mes = int(data_str[4:6])
                    dia = int(data_str[6:8])
                    hora = int(hora_str[:2])
                    minuto = int(hora_str[2:4])
                    data = datetime(ano, mes, dia, hora, minuto)
                    datas_arquivos.append((arquivo, data))
        except Exception as e:
            continue
    
    if datas_arquivos:
        datas_arquivos.sort(key=lambda x: x[1])
        data_mais_antiga = datas_arquivos[0][1]
        data_mais_recente = datas_arquivos[-1][1]
        print(f"   Data mais antiga: {data_mais_antiga.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Data mais recente: {data_mais_recente.strftime('%d/%m/%Y %H:%M')}")
    else:
        print("   ⚠️ Não foi possível extrair datas dos nomes dos arquivos")
    
    print()
    
    # 4. Analisar datas do consolidado
    if not df_consolidado.empty and 'timestamp' in df_consolidado.columns:
        print("📅 Analisando datas do arquivo consolidado...")
        df_consolidado['timestamp_numeric'] = pd.to_numeric(df_consolidado['timestamp'], errors='coerce')
        df_consolidado['data_avaliacao'] = pd.to_datetime(df_consolidado['timestamp_numeric'], unit='s', errors='coerce')
        
        df_validos = df_consolidado[df_consolidado['data_avaliacao'].notna()]
        
        if not df_validos.empty:
            data_mais_antiga_consolidado = df_validos['data_avaliacao'].min()
            data_mais_recente_consolidado = df_validos['data_avaliacao'].max()
            print(f"   Data mais antiga: {data_mais_antiga_consolidado.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   Data mais recente: {data_mais_recente_consolidado.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Comparar com arquivos individuais
            if datas_arquivos:
                if data_mais_recente_consolidado < data_mais_recente:
                    print()
                    print("⚠️ ATENÇÃO: O arquivo consolidado está desatualizado!")
                    print(f"   Consolidado mais recente: {data_mais_recente_consolidado.strftime('%d/%m/%Y %H:%M:%S')}")
                    print(f"   Arquivo individual mais recente: {data_mais_recente.strftime('%d/%m/%Y %H:%M')}")
                    print()
                    return True  # Precisa regenerar
        else:
            print("   ⚠️ Nenhuma data válida encontrada no consolidado")
    else:
        print("   ⚠️ Consolidado vazio ou sem coluna 'timestamp'")
        if arquivos_avaliacao:
            print()
            print("⚠️ ATENÇÃO: Existem arquivos individuais mas o consolidado está vazio!")
            print()
            return True  # Precisa regenerar
    
    print()
    print("✅ O arquivo consolidado parece estar atualizado")
    print()
    return False  # Não precisa regenerar

def regenerar_consolidado(periodo: str = None):
    """
    Regenera o arquivo consolidado a partir de todos os arquivos individuais.
    
    Args:
        periodo: Período acadêmico (ex: "2025-2A", "2025-2B"). Se None, usa o período atual.
    """
    if periodo is None:
        periodo = get_current_period()
    
    print("=" * 80)
    print(f"🔄 REGENERAÇÃO DO ARQUIVO CONSOLIDADO - {periodo}")
    print("=" * 80)
    print()
    
    modelo = AvaliacaoModel()
    sucesso = modelo.regenerar_consolidado_de_todos_os_arquivos(periodo=periodo)
    
    if sucesso:
        print()
        print("✅ Regeneração concluída com sucesso!")
    else:
        print()
        print("❌ Erro na regeneração do arquivo consolidado")
    
    return sucesso

def main():
    """Função principal"""
    import sys
    
    print()
    print("🔍 VERIFICAÇÃO E ATUALIZAÇÃO DO ARQUIVO CONSOLIDADO")
    print()
    
    # Verificar período atual ou usar argumento da linha de comando
    periodo = get_current_period()
    
    # Se houver argumento na linha de comando, usar ele
    if len(sys.argv) > 1:
        periodo = sys.argv[1]
        print(f"📅 Período especificado: {periodo}")
    else:
        print(f"📅 Período atual configurado: {periodo}")
    
    # Se houver segundo argumento "auto", regenerar automaticamente
    auto_regenerar = len(sys.argv) > 2 and sys.argv[2].lower() == "auto"
    
    print()
    
    # Verificar estado do consolidado
    precisa_regenerar = verificar_consolidado(periodo)
    
    if precisa_regenerar:
        print()
        if auto_regenerar:
            print("🔄 Regenerando automaticamente...")
            print()
            regenerar_consolidado(periodo)
        else:
            print("⚠️ O arquivo consolidado precisa ser regenerado.")
            print("   Execute: python verificar_e_atualizar_consolidado.py [periodo] auto")
            print("   para regenerar automaticamente.")
    else:
        print()
        if auto_regenerar:
            print("🔄 Regenerando mesmo assim (modo auto)...")
            print()
            regenerar_consolidado(periodo)
        else:
            print("✅ O arquivo consolidado está atualizado.")
            print("   Se quiser regenerar mesmo assim, execute:")
            print("   python verificar_e_atualizar_consolidado.py [periodo] auto")
    
    print()
    print("=" * 80)
    print("✅ Verificação concluída!")
    print("=" * 80)

if __name__ == "__main__":
    main()

