#!/usr/bin/env python3
"""
Script para calcular as notas finais da Sprint 5 por turma e grupo
"""

from src.utils.busca_direta_supabase import buscar_avaliacoes_por_turma_sprint
import pandas as pd
import json

def carregar_config():
    """Carrega configurações"""
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_alunos(periodo: str = "2025-2A"):
    """
    Carrega dados dos alunos para um período específico
    
    Args:
        periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
    """
    with open('data/alunos.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
        # Nova estrutura: {periodo: {T09: {...}, T13: {...}}}
        if periodo in dados and isinstance(dados[periodo], dict):
            return dados[periodo]
        return {}

def carregar_usuarios():
    """Carrega dados dos usuários"""
    with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def obter_nome_aluno(id_aluno, turma, usuarios_data):
    """Obtém o nome do aluno pelo ID"""
    for email, dados in usuarios_data.items():
        if dados.get('id') == id_aluno and dados.get('turma') == turma:
            return dados.get('name', 'Desconhecido')
    return f"ID_{id_aluno}"

def calcular_nota_final(total_aluno, media_geral, amplitude):
    """
    Calcula a nota final usando a fórmula:
    Nota Final = (Total do Aluno - Média Geral) / (0.6 × Amplitude)
    """
    if amplitude == 0:
        return 0
    
    nota_final = (total_aluno - media_geral) / (0.6 * amplitude)
    return round(nota_final, 2)

def processar_turma_sprint(turma, sprint="Sprint 5"):
    """Processa uma turma e sprint específica"""
    print(f"\n{'='*100}")
    print(f"🎯 TURMA {turma} - {sprint}")
    print(f"{'='*100}\n")
    
    print(f"⏳ Buscando avaliações de {turma}...")
    
    # Buscar avaliações
    df = buscar_avaliacoes_por_turma_sprint(turma, sprint)
    
    print(f"✅ Busca concluída!")
    
    if df.empty:
        print(f"❌ Nenhuma avaliação encontrada para {turma} - {sprint}")
        return
    
    # Carregar dados
    config = carregar_config()
    alunos_data = carregar_alunos()
    usuarios_data = carregar_usuarios()
    
    # Pegar apenas a última avaliação de cada avaliador para cada avaliado em cada eixo
    df_sorted = df.sort_values('timestamp')
    df_last = df_sorted.groupby(['id_avaliador', 'id_avaliado', 'eixo'], as_index=False).last()
    
    print(f"📊 Total de avaliações (após deduplicação): {len(df_last)}")
    print(f"📊 Sprints incluídas: {sorted(df_last['sprint'].unique())}")
    
    # Verificar quantas vieram da Sprint 4 (corrigidas para Sprint 5)
    sprint_4_count = len(df_last[df_last['sprint'] == 'Sprint 4'])
    sprint_5_count = len(df_last[df_last['sprint'] == 'Sprint 5'])
    
    if sprint_4_count > 0:
        print(f"📊 Avaliações Sprint 4 (após 06/10, consideradas Sprint 5): {sprint_4_count}")
    print(f"📊 Avaliações Sprint 5 original: {sprint_5_count}")
    
    # Agrupar por grupo
    grupos = sorted(df_last['time'].unique())
    
    for grupo in grupos:
        df_grupo = df_last[df_last['time'] == grupo]
        
        print(f"\n{'='*100}")
        print(f"📦 {turma} - {grupo}")
        print(f"{'='*100}\n")
        
        # Calcular somatório de notas recebidas por aluno
        notas_por_aluno = {}
        
        for id_aluno in df_grupo['id_avaliado'].unique():
            df_aluno = df_grupo[df_grupo['id_avaliado'] == id_aluno]
            total_notas = df_aluno['nota'].sum()
            nome_aluno = df_aluno['nome_avaliado'].iloc[0] if not df_aluno.empty else obter_nome_aluno(id_aluno, turma, usuarios_data)
            
            # Calcular notas por eixo
            notas_por_eixo = {}
            for eixo in df_aluno['eixo'].unique():
                df_eixo = df_aluno[df_aluno['eixo'] == eixo]
                notas_por_eixo[eixo] = df_eixo['nota'].sum()
            
            notas_por_aluno[id_aluno] = {
                'nome': nome_aluno,
                'total': total_notas,
                'eixos': notas_por_eixo
            }
        
        # Calcular estatísticas do grupo
        if notas_por_aluno:
            totais = [dados['total'] for dados in notas_por_aluno.values()]
            media_geral = sum(totais) / len(totais)
            max_nota = max(totais)
            min_nota = min(totais)
            amplitude = max_nota - min_nota
            
            print(f"📊 Estatísticas do Grupo:")
            print(f"   Média Geral: {media_geral:.2f}")
            print(f"   Nota Máxima: {max_nota}")
            print(f"   Nota Mínima: {min_nota}")
            print(f"   Amplitude: {amplitude}")
            print(f"\n{'─'*100}")
            print(f"{'Aluno':<40} {'Entregas':<12} {'Valor':<12} {'Ferramentas':<15} {'Total':<8} {'Nota Final':<12}")
            print(f"{'─'*100}")
            
            # Ordenar por total de pontos (decrescente)
            alunos_ordenados = sorted(notas_por_aluno.items(), key=lambda x: x[1]['total'], reverse=True)
            
            for id_aluno, dados in alunos_ordenados:
                nome = dados['nome'][:38]  # Limitar tamanho do nome
                eixos = dados['eixos']
                total = dados['total']
                
                # Pegar notas por eixo (alguns eixos podem ter nomes variados)
                entregas = 0
                valor = 0
                ferramentas = 0
                
                for eixo_nome, nota in eixos.items():
                    eixo_lower = eixo_nome.lower()
                    if 'entrega' in eixo_lower or 'real' in eixo_lower:
                        entregas += nota
                    elif 'valor' in eixo_lower or 'perceb' in eixo_lower:
                        valor += nota
                    elif 'ferramenta' in eixo_lower or 'caixa' in eixo_lower:
                        ferramentas += nota
                
                # Calcular nota final
                nota_final = calcular_nota_final(total, media_geral, amplitude)
                
                print(f"{nome:<40} {entregas:<12} {valor:<12} {ferramentas:<15} {total:<8} {nota_final:<12}")
            
            print(f"{'─'*100}\n")
            
            # Mostrar fórmula
            print(f"📐 Fórmula da Nota Final:")
            print(f"   Nota Final = (Total do Aluno - Média Geral) / (0.6 × Amplitude)")
            print(f"   Nota Final = (Total - {media_geral:.2f}) / (0.6 × {amplitude})")
            print(f"   Nota Final = (Total - {media_geral:.2f}) / {0.6 * amplitude:.2f}")
        else:
            print("❌ Nenhum dado encontrado para este grupo")

def main():
    print("🔢 CÁLCULO DE NOTAS FINAIS - SPRINT 5 - T13")
    print("="*100)
    
    # Processar apenas T13
    processar_turma_sprint("T13", "Sprint 5")
    
    print(f"\n{'='*100}")
    print("✅ Processamento concluído!")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()

