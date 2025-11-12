#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar diferentes parametrizações da fórmula de cálculo de notas
Permite experimentar diferentes valores de K e diferentes fórmulas
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import json
import os
import tempfile
from src.utils.supabase_storage import download_json_from_bucket, get_bucket_for_period

def calcular_k_por_tamanho_grupo(n: int, k_map: dict) -> int:
    """Calcula K baseado no tamanho do grupo usando um mapa customizado"""
    return k_map.get(n, k_map.get(7, 54))  # Default para N=7

def calcular_indice_formula_original(px: float, p_medio: float, p_max: float, p_min: float, k: int) -> float:
    """Fórmula original: Índice = (Px - Pmédi) / ((Pmax - Pmin) + K)"""
    denominador = (p_max - p_min) + k
    if denominador == 0:
        return 0.0
    return round((px - p_medio) / denominador, 2)

def calcular_indice_formula_com_fator(px: float, p_medio: float, p_max: float, p_min: float, k: int, fator: float) -> float:
    """Fórmula com fator multiplicador: Índice = fator * (Px - Pmédi) / ((Pmax - Pmin) + K)"""
    denominador = (p_max - p_min) + k
    if denominador == 0:
        return 0.0
    return round(fator * (px - p_medio) / denominador, 2)

def calcular_indice_formula_k_reduzido(px: float, p_medio: float, p_max: float, p_min: float, k: int, fator_k: float) -> float:
    """Fórmula com K reduzido: Índice = (Px - Pmédi) / ((Pmax - Pmin) + K*fator_k)"""
    denominador = (p_max - p_min) + (k * fator_k)
    if denominador == 0:
        return 0.0
    return round((px - p_medio) / denominador, 2)

def calcular_indice_formula_normalizada(px: float, p_medio: float, p_max: float, p_min: float, amplitude: float) -> float:
    """Fórmula normalizada para -0.6 a +0.6: Índice = 0.6 * (Px - Pmédi) / amplitude_max"""
    if amplitude == 0:
        return 0.0
    # Normalizar para que o máximo seja 0.6
    indice_raw = (px - p_medio) / amplitude
    # Garantir que fique entre -0.6 e +0.6
    indice_normalizado = max(-0.6, min(0.6, indice_raw * 0.6))
    return round(indice_normalizado, 2)

def calcular_indice_formula_com_limite(px: float, p_medio: float, p_max: float, p_min: float, k: int, fator: float, limite: float = 0.6) -> float:
    """Fórmula híbrida com limite: Índice = min(limite, max(-limite, fator × (Px - Pmédi) / ((Pmax - Pmin) + K)))"""
    denominador = (p_max - p_min) + k
    if denominador == 0:
        return 0.0
    indice_calculado = fator * (px - p_medio) / denominador
    # Limitar entre -limite e +limite
    indice_limitado = max(-limite, min(limite, indice_calculado))
    return round(indice_limitado, 2)

def carregar_dados_t13_sprint2():
    """Carrega dados da T13 Sprint 2 do arquivo consolidado"""
    periodo = "2025-2B"
    turma = "T13"
    sprint = "Sprint 2"
    
    bucket_name = get_bucket_for_period(periodo)
    
    with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as tmp:
        download_json_from_bucket('avaliacoescompletas_consolidadas.json', tmp.name, bucket_name=bucket_name)
        tmp.seek(0)
        conteudo = tmp.read().decode("utf-8").strip()
        
        if not conteudo:
            return pd.DataFrame()
        
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
    
    try:
        os.unlink(tmp.name)
    except:
        pass
    
    # Filtrar por turma e sprint
    if not df.empty:
        df = df[(df['turma'] == turma) & (df['sprint'] == sprint)]
    
    return df

def processar_grupo_com_formulas(df_grupo, grupo_nome, n_alunos, formulas_config):
    """Processa um grupo aplicando diferentes fórmulas"""
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
    
    if not notas_por_aluno:
        return None
    
    totais = [dados['total'] for dados in notas_por_aluno.values()]
    media_geral = sum(totais) / len(totais)
    max_nota = max(totais)
    min_nota = min(totais)
    amplitude = max_nota - min_nota
    
    resultados = {
        'grupo': grupo_nome,
        'n': n_alunos,
        'media': media_geral,
        'max': max_nota,
        'min': min_nota,
        'amplitude': amplitude,
        'alunos': notas_por_aluno,
        'formulas': {}
    }
    
    # Aplicar cada fórmula configurada
    for nome_formula, config in formulas_config.items():
        k = config.get('k', calcular_k_por_tamanho_grupo(n_alunos, config.get('k_map', {})))
        formula_func = config['funcao']
        params = config.get('params', {})
        
        indices = {}
        for id_aluno, dados in notas_por_aluno.items():
            px = dados['total']
            if 'limite' in params:
                # Fórmula com limite
                indice = formula_func(px, media_geral, max_nota, min_nota, k, params['fator'], params['limite'])
            elif 'fator' in params and 'normalizada' not in params:
                # Fórmula com fator (sem limite)
                indice = formula_func(px, media_geral, max_nota, min_nota, k, params['fator'])
            elif 'fator_k' in params:
                # Fórmula com K reduzido
                indice = formula_func(px, media_geral, max_nota, min_nota, k, params['fator_k'])
            elif 'normalizada' in params and params['normalizada']:
                # Fórmula normalizada
                indice = formula_func(px, media_geral, max_nota, min_nota, amplitude)
            else:
                # Fórmula original
                indice = formula_func(px, media_geral, max_nota, min_nota, k)
            indices[id_aluno] = indice
        
        resultados['formulas'][nome_formula] = {
            'k': k,
            'indices': indices,
            'min_indice': min(indices.values()) if indices else 0,
            'max_indice': max(indices.values()) if indices else 0,
            'amplitude_indices': max(indices.values()) - min(indices.values()) if indices else 0
        }
    
    return resultados

def main():
    print("="*120)
    print("TESTE DE PARAMETRIZACOES DA FORMULA DE CALCULO DE NOTAS")
    print("="*120)
    print()
    
    # Carregar dados
    print("Carregando dados da T13 - Sprint 2...")
    df = carregar_dados_t13_sprint2()
    
    if df.empty:
        print("ERRO: Nenhum dado encontrado")
        return
    
    # Deduplicar
    df_sorted = df.sort_values('timestamp')
    df_last = df_sorted.groupby(['id_avaliador', 'id_avaliado', 'eixo'], as_index=False).last()
    
    print(f"Total de avaliacoes: {len(df_last)}")
    print()
    
    # Carregar estrutura de grupos
    with open('data/alunos.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
        grupos_data = dados["2025-2B"]["T13"]
    
    # Definir diferentes configurações de fórmulas para testar
    formulas_config = {
        'Original (K atual)': {
            'funcao': calcular_indice_formula_original,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {}
        },
        'K reduzido (50%)': {
            'funcao': calcular_indice_formula_k_reduzido,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator_k': 0.5}
        },
        'K reduzido (25%)': {
            'funcao': calcular_indice_formula_k_reduzido,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator_k': 0.25}
        },
        'K reduzido (15%)': {
            'funcao': calcular_indice_formula_k_reduzido,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator_k': 0.15}
        },
        'K reduzido (10%)': {
            'funcao': calcular_indice_formula_k_reduzido,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator_k': 0.1}
        },
        'Com fator 5x': {
            'funcao': calcular_indice_formula_com_fator,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 5.0}
        },
        'Com fator 7x': {
            'funcao': calcular_indice_formula_com_fator,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 7.0}
        },
        'Com fator 7.5x': {
            'funcao': calcular_indice_formula_com_fator,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 7.5}
        },
        'Com fator 8x': {
            'funcao': calcular_indice_formula_com_fator,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 8.0}
        },
        'Com fator 10x': {
            'funcao': calcular_indice_formula_com_fator,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 10.0}
        },
        'Fator 7.5x com limite 0.6': {
            'funcao': calcular_indice_formula_com_limite,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 7.5, 'limite': 0.6}
        },
        'Fator 8x com limite 0.6': {
            'funcao': calcular_indice_formula_com_limite,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 8.0, 'limite': 0.6}
        },
        'Fator 10x com limite 0.6': {
            'funcao': calcular_indice_formula_com_limite,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 10.0, 'limite': 0.6}
        },
        'Fator 7.5x com limite 0.5': {
            'funcao': calcular_indice_formula_com_limite,
            'k_map': {4: 9, 5: 14, 6: 44, 7: 54, 8: 99},
            'params': {'fator': 7.5, 'limite': 0.5}
        },
        'Normalizada (-0.6 a +0.6)': {
            'funcao': calcular_indice_formula_normalizada,
            'k_map': {},
            'params': {'normalizada': True}
        }
    }
    
    # Processar cada grupo
    grupos_avaliacao = sorted(df_last['time'].unique())
    
    resultados_gerais = {}
    
    for grupo in grupos_avaliacao:
        df_grupo = df_last[df_last['time'] == grupo]
        n_alunos = len(grupos_data[grupo])
        
        resultado = processar_grupo_com_formulas(df_grupo, grupo, n_alunos, formulas_config)
        if resultado:
            resultados_gerais[grupo] = resultado
    
    # Exibir resultados
    print("="*120)
    print("RESULTADOS COMPARATIVOS")
    print("="*120)
    print()
    
    for grupo_nome, resultado in resultados_gerais.items():
        print(f"\n{'='*120}")
        print(f"GRUPO: {grupo_nome} (N={resultado['n']})")
        print(f"{'='*120}")
        print(f"Estatisticas: Media={resultado['media']:.2f}, Max={resultado['max']}, Min={resultado['min']}, Amplitude={resultado['amplitude']}")
        print()
        
        # Tabela comparativa (ajustar largura para mais colunas)
        print(f"{'Aluno':<35} ", end="")
        for nome_formula in formulas_config.keys():
            # Reduzir tamanho do nome da fórmula para caber mais colunas
            nome_curto = nome_formula[:12] if len(nome_formula) > 12 else nome_formula
            print(f"{nome_curto:<15}", end="")
        print()
        print("-" * 200)
        
        # Ordenar alunos por total
        alunos_ordenados = sorted(resultado['alunos'].items(), key=lambda x: x[1]['total'], reverse=True)
        
        for id_aluno, dados_aluno in alunos_ordenados:
            nome = dados_aluno['nome'][:33]
            print(f"{nome:<35} ", end="")
            for nome_formula in formulas_config.keys():
                indice = resultado['formulas'][nome_formula]['indices'][id_aluno]
                print(f"{indice:>7.2f}      ", end="")
            print()
        
        print("-" * 200)
        print(f"{'Min Indice':<35} ", end="")
        for nome_formula in formulas_config.keys():
            min_i = resultado['formulas'][nome_formula]['min_indice']
            print(f"{min_i:>7.2f}      ", end="")
        print()
        
        print(f"{'Max Indice':<35} ", end="")
        for nome_formula in formulas_config.keys():
            max_i = resultado['formulas'][nome_formula]['max_indice']
            print(f"{max_i:>7.2f}      ", end="")
        print()
        
        print(f"{'Amplitude Indices':<35} ", end="")
        for nome_formula in formulas_config.keys():
            amp_i = resultado['formulas'][nome_formula]['amplitude_indices']
            print(f"{amp_i:>7.2f}      ", end="")
        print()
        print()
    
    # Resumo geral
    print("\n" + "="*120)
    print("RESUMO GERAL - AMPLITUDE DOS INDICES POR FORMULA")
    print("="*120)
    print()
    
    print(f"{'Formula':<30} {'Min Geral':<15} {'Max Geral':<15} {'Amplitude Media':<20}")
    print("-" * 80)
    
    for nome_formula in formulas_config.keys():
        min_geral = min([r['formulas'][nome_formula]['min_indice'] for r in resultados_gerais.values()])
        max_geral = max([r['formulas'][nome_formula]['max_indice'] for r in resultados_gerais.values()])
        amp_media = sum([r['formulas'][nome_formula]['amplitude_indices'] for r in resultados_gerais.values()]) / len(resultados_gerais)
        
        print(f"{nome_formula:<30} {min_geral:>8.2f}      {max_geral:>8.2f}      {amp_media:>8.2f}")
    
    print("\n" + "="*120)
    print("SUGESTOES BASEADAS NOS RESULTADOS")
    print("="*120)
    print()
    print("Objetivo: Intervalo de aproximadamente -0.6 a +0.6")
    print()
    print("Analise os resultados acima e escolha a parametrizacao que melhor")
    print("atende ao objetivo de ter indices entre -0.6 e +0.6 com distancias")
    print("significativas entre os alunos.")
    print()

if __name__ == "__main__":
    main()

