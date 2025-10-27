#!/usr/bin/env python3
"""
Script para calcular as notas finais da Sprint 5 da T13
Busca diretamente pelos nomes dos arquivos
"""

from src.utils.supabase_storage import get_supabase_client, download_json_from_bucket
import pandas as pd
import json
import tempfile
import os
from datetime import datetime

def carregar_usuarios():
    """Carrega dados dos usuários"""
    with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def calcular_nota_final(total_aluno, media_geral, amplitude):
    """
    Calcula a nota final usando a fórmula:
    Nota Final = (Total do Aluno - Média Geral) / (0.6 × Amplitude)
    """
    if amplitude == 0:
        return 0
    
    nota_final = (total_aluno - media_geral) / (0.6 * amplitude)
    return round(nota_final, 2)

def main():
    print("🔢 CÁLCULO DE NOTAS FINAIS - SPRINT 5 - T13")
    print("="*100)
    
    # Listar todos os arquivos com paginação
    print("\n⏳ Listando todos os arquivos...")
    supabase = get_supabase_client()
    
    todos_arquivos = []
    offset = 0
    limit = 1000
    
    while True:
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
            break
        
        todos_arquivos.extend(arquivos)
        
        if len(arquivos) < limit:
            break
        
        offset += len(arquivos)
    
    print(f"✅ Total de arquivos: {len(todos_arquivos)}")
    
    # Filtrar arquivos da T13
    arquivos_t13 = [f for f in todos_arquivos if f["name"].startswith("aval_T13_") and f["name"].endswith(".json")]
    print(f"✅ Arquivos da T13: {len(arquivos_t13)}")
    
    # Data de início da avaliação de pares da Sprint 5: 06/10/2025
    data_inicio_sprint5 = datetime(2025, 10, 6).timestamp()
    
    # Processar apenas arquivos da Sprint 5 OU Sprint 4 criados após 06/10
    todos_dados = []
    
    print(f"\n⏳ Processando arquivos da T13...")
    
    for i, arq in enumerate(arquivos_t13):
        nome_arquivo = arq["name"]
        created_at = arq.get("created_at", "")
        
        # Verificar se é Sprint 5 OU Sprint 4 criado após 06/10
        is_sprint5 = "Sprint 5" in nome_arquivo or "Sprint5" in nome_arquivo
        
        is_sprint4_corrigido = False
        if "Sprint 4" in nome_arquivo or "Sprint4" in nome_arquivo:
            # Verificar data de criação
            if created_at:
                try:
                    data_criacao = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                    if data_criacao >= data_inicio_sprint5:
                        is_sprint4_corrigido = True
                except:
                    pass
        
        if is_sprint5 or is_sprint4_corrigido:
            if (i + 1) % 10 == 0:
                print(f"   Processando arquivo {i+1}/{len(arquivos_t13)}...")
            
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                    download_json_from_bucket(nome_arquivo, tmp_file.name)
                    
                    with open(tmp_file.name, 'r', encoding='utf-8') as f:
                        conteudo = f.read().strip()
                    
                    if conteudo:
                        for linha in conteudo.splitlines():
                            linha = linha.strip()
                            if linha:
                                try:
                                    dado = json.loads(linha)
                                    if isinstance(dado, dict) and 'timestamp' in dado:
                                        todos_dados.append(dado)
                                except:
                                    continue
                    
                    try:
                        os.unlink(tmp_file.name)
                    except:
                        pass
                        
            except Exception as e:
                continue
    
    print(f"✅ Processamento concluído! Total de registros: {len(todos_dados)}")
    
    if not todos_dados:
        print("❌ Nenhum dado encontrado")
        return
    
    # Criar DataFrame
    df = pd.DataFrame(todos_dados)
    
    # Remover duplicatas
    df = df.drop_duplicates(subset=['timestamp', 'id_avaliador', 'id_avaliado', 'eixo'], keep='last')
    
    print(f"📊 Total após deduplicação: {len(df)}")
    print(f"📊 Sprints incluídas: {sorted(df['sprint'].unique())}")
    
    # Mostrar quantas vieram da Sprint 4
    sprint_4_count = len(df[df['sprint'] == 'Sprint 4'])
    sprint_5_count = len(df[df['sprint'] == 'Sprint 5'])
    
    if sprint_4_count > 0:
        print(f"📊 Avaliações Sprint 4 (após 06/10): {sprint_4_count}")
    print(f"📊 Avaliações Sprint 5 original: {sprint_5_count}")
    
    # Carregar dados de usuários
    usuarios_data = carregar_usuarios()
    
    # Processar por grupo
    grupos = sorted(df['time'].unique())
    
    for grupo in grupos:
        df_grupo = df[df['time'] == grupo]
        
        print(f"\n{'='*100}")
        print(f"📦 T13 - {grupo}")
        print(f"{'='*100}\n")
        
        # Calcular somatório de notas recebidas por aluno
        notas_por_aluno = {}
        
        for id_aluno in df_grupo['id_avaliado'].unique():
            df_aluno = df_grupo[df_grupo['id_avaliado'] == id_aluno]
            total_notas = df_aluno['nota'].sum()
            nome_aluno = df_aluno['nome_avaliado'].iloc[0] if not df_aluno.empty else f"ID_{id_aluno}"
            
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
                nome = dados['nome'][:38]
                eixos = dados['eixos']
                total = dados['total']
                
                # Pegar notas por eixo
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
            print(f"   Nota Final = (Total - {media_geral:.2f}) / {0.6 * amplitude:.2f}\n")
        else:
            print("❌ Nenhum dado encontrado para este grupo")
    
    print(f"\n{'='*100}")
    print("✅ Processamento concluído!")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
