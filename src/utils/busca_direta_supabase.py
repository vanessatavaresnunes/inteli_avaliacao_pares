"""
Módulo para busca direta de avaliações no Supabase por turma e sprint
"""

import json
import tempfile
import os
from datetime import datetime
from src.utils.supabase_storage import download_json_from_bucket, list_json_files_in_bucket, get_bucket_for_period
import pandas as pd


def carregar_datas_sprints(periodo: str = "2026-1A"):
    """
    Carrega as datas das sprints do arquivo de configuração
    
    Args:
        periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
    """
    try:
        # Determinar qual arquivo carregar baseado no período
        if periodo == "2025-2B":
            arquivo = 'data/sprint_dates_2025_2b.json'
        else:
            arquivo = 'data/sprint_dates_2025_2a.json'
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados['sprints']
    except Exception as e:
        print(f"Erro ao carregar datas das sprints do período {periodo}: {e}")
        return {}


def buscar_avaliacoes_por_turma_sprint(turma, sprint, periodo: str = "2026-1A"):
    """
    Busca avaliações diretamente no Supabase filtrando por turma e sprint.
    Para Sprint 5, também considera a data de início da avaliação de pares.
    
    Args:
        turma: Turma (ex: 'T13', 'T09')
        sprint: Sprint (ex: 'Sprint 1', 'Sprint 2', etc.)
        periodo: Período acadêmico (ex: '2025-2A', '2025-2B')
    
    Returns:
        DataFrame com as avaliações encontradas
    """
    print(f"\n🔍 Buscando avaliações - Turma: {turma}, Sprint: {sprint}, Período: {periodo}")
    
    # Determinar qual bucket usar baseado no período
    bucket_name = get_bucket_for_period(periodo)
    print(f"📦 Usando bucket: {bucket_name}")
    
    # Carregar datas das sprints para o período correto
    sprints_config = carregar_datas_sprints(periodo)
    
    # Listar TODOS os arquivos usando paginação
    from src.utils.supabase_storage import get_supabase_client
    supabase = get_supabase_client()
    
    todos_arquivos = []
    offset = 0
    limit = 1000
    
    print("🔄 Buscando arquivos com paginação...")
    
    while True:
        try:
            arquivos = supabase.storage.from_(bucket_name).list(
                path="",
                options={
                    "limit": limit,
                    "offset": offset,
                    "sortBy": {"column": "created_at", "order": "desc"}
                }
            )
            
            if not arquivos:
                break
            
            todos_arquivos.extend(arquivos)
            
            if len(arquivos) < limit:
                break
            
            offset += len(arquivos)
            
        except Exception as e:
            print(f"❌ Erro na paginação: {e}")
            break
    
    print(f"📋 Total de arquivos encontrados: {len(todos_arquivos)}")
    
    # Filtrar apenas arquivos de avaliação da turma
    arquivos_turma = [f["name"] for f in todos_arquivos if f["name"].startswith(f'aval_{turma}_') and f["name"].endswith('.json')]
    print(f"📋 Arquivos da {turma}: {len(arquivos_turma)}")
    
    if len(arquivos_turma) == 0:
        print(f"❌ Nenhum arquivo encontrado para {turma}")
        return pd.DataFrame()
    
    # Baixar e processar arquivos
    todos_dados = []
    
    # Obter data de início da avaliação de pares para Sprint 5
    data_inicio_avalpares = None
    if sprint == "Sprint 5":
        sprint_key = "sprint_5"
        if sprint_key in sprints_config and "data_avalpares_inicio" in sprints_config[sprint_key]:
            data_inicio_avalpares = datetime.strptime(
                sprints_config[sprint_key]["data_avalpares_inicio"], 
                "%Y-%m-%d"
            ).timestamp()
            print(f"📅 Data início avaliação pares Sprint 5: {sprints_config[sprint_key]['data_avalpares_inicio']}")
    
    for arquivo in arquivos_turma:
        try:
            print(f"📥 Processando {arquivo}...")
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                download_json_from_bucket(arquivo, tmp_file.name)
                
                # Ler o arquivo baixado
                with open(tmp_file.name, 'r', encoding='utf-8') as f:
                    conteudo = f.read().strip()
                
                if conteudo:
                    # Processar cada linha do arquivo
                    for linha in conteudo.splitlines():
                        linha = linha.strip()
                        if linha:
                            try:
                                dado = json.loads(linha)
                                
                                # Validar se o dado tem os campos essenciais
                                if isinstance(dado, dict) and 'timestamp' in dado:
                                    # Filtrar por sprint
                                    if 'sprint' in dado:
                                        sprint_arquivo = dado['sprint']
                                        
                                        # Para Sprint 5, aceitar também Sprint 4 se a data for posterior ao início da avaliação
                                        if sprint == "Sprint 5" and data_inicio_avalpares:
                                            timestamp_arquivo = dado.get('timestamp', 0)
                                            
                                            # Aceitar se for Sprint 5 OU (Sprint 4 E data >= data_inicio_avalpares)
                                            if sprint_arquivo == sprint or \
                                               (sprint_arquivo == "Sprint 4" and timestamp_arquivo >= data_inicio_avalpares):
                                                todos_dados.append(dado)
                                        else:
                                            # Para outras sprints, filtrar normalmente
                                            if sprint_arquivo == sprint:
                                                todos_dados.append(dado)
                                                
                            except json.JSONDecodeError as e:
                                print(f"⚠️ Erro JSON: {e}")
                                continue
                
                # Limpar arquivo temporário
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass  # Ignorar erros ao excluir arquivo temporário
                
        except Exception as e:
            print(f"❌ Erro ao processar {arquivo}: {e}")
            continue
    
    if not todos_dados:
        print(f"❌ Nenhum dado encontrado para {turma} - {sprint}")
        return pd.DataFrame()
    
    # Criar DataFrame
    df = pd.DataFrame(todos_dados)
    
    # Remover duplicatas baseadas em timestamp, id_avaliador, id_avaliado, eixo
    print(f"📊 Total de registros antes da deduplicação: {len(df)}")
    df = df.drop_duplicates(
        subset=['timestamp', 'id_avaliador', 'id_avaliado', 'eixo'],
        keep='last'
    )
    print(f"📊 Total de registros após deduplicação: {len(df)}")
    
    # Ordenar por timestamp
    df = df.sort_values('timestamp')
    
    print(f"✅ Total de registros encontrados: {len(df)}")
    return df


def buscar_arquivos_especificos_turma(turma, sprint):
    """
    Tenta buscar arquivos específicos de uma turma quando a listagem geral não os encontra.
    Usa uma estratégia de busca por nome conhecido.
    """
    from src.utils.supabase_storage import get_supabase_client
    
    arquivos_encontrados = []
    
    # Tentar diferentes variações de nomes de arquivo
    # Padrão: aval_T13_Grupo X_Sprint Y_ID_YYYYMMDD_HHMM.json
    
    # Buscar por prefixo específico
    try:
        supabase = get_supabase_client()
        
        # Tentar buscar com diferentes prefixos
        prefixos = [
            f"aval_{turma}_Grupo 1_{sprint}",
            f"aval_{turma}_Grupo 2_{sprint}",
            f"aval_{turma}_Grupo 3_{sprint}",
            f"aval_{turma}_Grupo 4_{sprint}",
            f"aval_{turma}_Grupo 5_{sprint}",
            f"aval_{turma}_Grupo 6_{sprint}",
        ]
        
        # Listar arquivos e filtrar pelos prefixos
        # Use bucket padrão (2026-1A) por enquanto
        bucket_name = get_bucket_for_period("2026-1A")
        arquivos_base = supabase.storage.from_(bucket_name).list()
        
        for arquivo in arquivos_base:
            nome = arquivo["name"]
            for prefixo in prefixos:
                if nome.startswith(prefixo):
                    arquivos_encontrados.append(nome)
                    break
        
        print(f"📋 Arquivos específicos encontrados: {len(arquivos_encontrados)}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar arquivos específicos: {e}")
    
    return arquivos_encontrados

