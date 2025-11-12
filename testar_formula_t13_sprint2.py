#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a nova fórmula de cálculo de notas para T13 - Sprint 2
Mostra o tamanho de cada grupo (N), o K usado e a fórmula aplicada
"""

import sys
import io
# Configurar encoding UTF-8 para stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.utils.busca_direta_supabase import buscar_avaliacoes_por_turma_sprint
import json
import os

def calcular_k_por_tamanho_grupo(n: int) -> int:
    """
    Calcula o valor de K (lastro) baseado no tamanho do grupo N.
    
    Valores de K para o período 2025-2B:
    - N=4 → K=9
    - N=5 → K=14
    - N=6 → K=44
    - N=7 → K=54
    - N=8 → K=99
    """
    k_map = {
        4: 9,
        5: 14,
        6: 44,
        7: 54,
        8: 99
    }
    return k_map.get(n, 54)  # Default para N=7 se não estiver no mapa

def carregar_alunos_2025_2b():
    """Carrega dados dos alunos do período 2025-2B"""
    with open('data/alunos.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
        if "2025-2B" in dados and "T13" in dados["2025-2B"]:
            return dados["2025-2B"]["T13"]
        return {}

def main():
    print("="*100)
    print("TESTE DA NOVA FORMULA - T13 - SPRINT 2")
    print("="*100)
    print()
    
    # Definir período como 2025-2B para usar a nova fórmula
    periodo = "2025-2B"
    turma = "T13"
    sprint = "Sprint 2"
    
    print(f"Periodo: {periodo}")
    print(f"Turma: {turma}")
    print(f"Sprint: {sprint}")
    print()
    
    # Carregar estrutura de grupos
    grupos_data = carregar_alunos_2025_2b()
    
    if not grupos_data:
        print("ERRO: Nao foi possivel carregar os dados dos grupos da T13 para 2025-2B")
        return
    
    print("ESTRUTURA DOS GRUPOS (T13 - 2025-2B):")
    print("-" * 100)
    
    # Mostrar tamanho de cada grupo e K correspondente
    for grupo_nome in sorted(grupos_data.keys()):
        alunos_ids = grupos_data[grupo_nome]
        n = len(alunos_ids)
        k = calcular_k_por_tamanho_grupo(n)
        
        print(f"\n{grupo_nome}:")
        print(f"  Tamanho do grupo (N): {n}")
        print(f"  K usado: {k}")
        print(f"  IDs dos alunos: {alunos_ids}")
    
    print("\n" + "="*100)
    print("FORMULA APLICADA:")
    print("="*100)
    print()
    print("Para o periodo 2025-2B, a formula e:")
    print("  Indice = (Px - Pmedi) / ((Pmax - Pmin) + K)")
    print()
    print("Onde:")
    print("  - Px = Pontos do aluno individual")
    print("  - Pmedi = Media dos pontos do grupo")
    print("  - Pmax = Maximo de pontos do grupo")
    print("  - Pmin = Minimo de pontos do grupo")
    print("  - K = Valor de lastro baseado no tamanho do grupo (N)")
    print()
    
    # Buscar avaliações do arquivo consolidado (mesmo método do analise.py)
    print("="*100)
    print("BUSCANDO AVALIACOES DA T13 - SPRINT 2...")
    print("="*100)
    print()
    
    try:
        import pandas as pd
        import tempfile
        from src.utils.supabase_storage import download_json_from_bucket, get_bucket_for_period
        
        # Carregar do arquivo consolidado (mesmo método do analise.py)
        bucket_name = get_bucket_for_period(periodo)
        print(f"Usando bucket: {bucket_name}")
        print("Carregando arquivo consolidado...")
        
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as tmp:
            download_json_from_bucket('avaliacoescompletas_consolidadas.json', tmp.name, bucket_name=bucket_name)
            tmp.seek(0)
            conteudo = tmp.read().decode("utf-8").strip()
            
            if not conteudo:
                print("AVISO: Arquivo consolidado esta vazio")
                return
            
            linhas = []
            for linha in conteudo.splitlines():
                linha = linha.strip()
                if linha:
                    try:
                        dado = json.loads(linha)
                        linhas.append(dado)
                    except Exception as e:
                        continue
            
            df = pd.DataFrame(linhas)
        
        # Limpar arquivo temporário
        try:
            os.unlink(tmp.name)
        except:
            pass
        
        # Filtrar por turma e sprint
        if not df.empty:
            df = df[(df['turma'] == turma) & (df['sprint'] == sprint)]
        
        if df.empty:
            print("AVISO: Nenhuma avaliacao encontrada para T13 - Sprint 2")
            print("   Verificando sprints disponiveis...")
            if not df.empty:
                sprints_disponiveis = sorted(df['sprint'].unique())
                print(f"   Sprints disponiveis na T13: {sprints_disponiveis}")
            return
        
        print(f"Total de avaliacoes encontradas: {len(df)}")
        print()
        
        # Pegar apenas a última avaliação de cada avaliador para cada avaliado em cada eixo
        df_sorted = df.sort_values('timestamp')
        df_last = df_sorted.groupby(['id_avaliador', 'id_avaliado', 'eixo'], as_index=False).last()
        
        print(f"Total apos deduplicacao: {len(df_last)}")
        print()
        
        # Agrupar por grupo
        grupos_avaliacao = sorted(df_last['time'].unique())
        
        print("="*100)
        print("RESULTADOS POR GRUPO:")
        print("="*100)
        print()
        
        for grupo in grupos_avaliacao:
            df_grupo = df_last[df_last['time'] == grupo]
            
            # Calcular somatório de notas recebidas por aluno
            notas_por_aluno = {}
            
            for id_aluno in df_grupo['id_avaliado'].unique():
                df_aluno = df_grupo[df_grupo['id_avaliado'] == id_aluno]
                total_notas = df_aluno['nota'].sum()
                nome_aluno = df_aluno['nome_avaliado'].iloc[0] if not df_aluno.empty else f"ID_{id_aluno}"
                
                notas_por_aluno[id_aluno] = {
                    'nome': nome_aluno,
                    'total': total_notas
                }
            
            if notas_por_aluno:
                totais = [dados['total'] for dados in notas_por_aluno.values()]
                media_geral = sum(totais) / len(totais)
                max_nota = max(totais)
                min_nota = min(totais)
                amplitude = max_nota - min_nota
                n_alunos = len(notas_por_aluno)
                k = calcular_k_por_tamanho_grupo(n_alunos)
                
                print(f"\n{'='*100}")
                print(f"{grupo}")
                print(f"{'='*100}")
                print()
                print(f"Tamanho do grupo (N): {n_alunos}")
                print(f"K usado: {k}")
                print()
                print(f"Estatisticas do Grupo:")
                print(f"   Media Geral (Pmedi): {media_geral:.2f}")
                print(f"   Maximo (Pmax): {max_nota}")
                print(f"   Minimo (Pmin): {min_nota}")
                print(f"   Amplitude (Pmax - Pmin): {amplitude}")
                print()
                print(f"Formula aplicada:")
                print(f"   Indice = (Px - {media_geral:.2f}) / (({max_nota} - {min_nota}) + {k})")
                print(f"   Indice = (Px - {media_geral:.2f}) / ({amplitude + k})")
                print()
                print(f"Alunos e seus indices calculados:")
                print(f"{'-'*100}")
                print(f"{'Aluno':<40} {'Total (Px)':<15} {'Indice':<15}")
                print(f"{'-'*100}")
                
                # Ordenar por total de pontos (decrescente)
                alunos_ordenados = sorted(notas_por_aluno.items(), key=lambda x: x[1]['total'], reverse=True)
                
                for id_aluno, dados in alunos_ordenados:
                    nome = dados['nome'][:38]
                    total = dados['total']
                    # Calcular índice usando a nova fórmula
                    denominador = amplitude + k
                    if denominador == 0:
                        indice = 0.0
                    else:
                        indice = round((total - media_geral) / denominador, 2)
                    
                    print(f"{nome:<40} {total:<15} {indice:<15}")
                
                print(f"{'-'*100}")
            else:
                print(f"\nAVISO: {grupo}: Nenhum dado encontrado")
        
        print("\n" + "="*100)
        print("Teste concluido!")
        print("="*100)
        
    except Exception as e:
        print(f"ERRO ao processar avaliacoes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

