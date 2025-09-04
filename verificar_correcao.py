#!/usr/bin/env python3
"""
Script para verificar se a correção funcionou.
"""

import sys
sys.path.append('src')

from utils.supabase_storage import download_json_from_bucket
import tempfile
import json
import os
import pandas as pd

def verificar_correcao():
    """Verifica se a correção funcionou"""
    print("✅ Verificando se a correção funcionou...")
    print("=" * 60)
    
    try:
        # Baixar arquivo consolidado atualizado
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as tmp:
            download_json_from_bucket('avaliacoescompletas_consolidadas.json', tmp.name)
            tmp.seek(0)
            conteudo = tmp.read().decode("utf-8").strip()
            
            if not conteudo:
                print("❌ Arquivo consolidado vazio")
                return
            
            # Processar dados
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
            print(f"📊 Total de registros no consolidado: {len(df)}")
            
            # Verificar ID 2 como avaliador
            id2_avaliador = df[df.get('id_avaliador') == 2]
            print(f"👤 Registros do ID 2 como avaliador: {len(id2_avaliador)}")
            
            if len(id2_avaliador) > 0:
                print("✅ ID 2 está no consolidado como avaliador!")
                
                # Verificar dados específicos
                t13_grupo3_sprint2 = id2_avaliador[
                    (id2_avaliador.get('turma') == 'T13') & 
                    (id2_avaliador.get('time') == 'Grupo 3') & 
                    (id2_avaliador.get('sprint') == 'Sprint 2')
                ]
                
                print(f"📊 Registros T13 Grupo 3 Sprint 2: {len(t13_grupo3_sprint2)}")
                
                if len(t13_grupo3_sprint2) > 0:
                    print("✅ ID 2 tem registros da T13 Grupo 3 Sprint 2!")
                    
                    # Mostrar alguns dados
                    print(f"📋 Dados do ID 2:")
                    for col in ['id_avaliador', 'nome_avaliador', 'time', 'turma', 'sprint', 'eixo', 'nota']:
                        if col in t13_grupo3_sprint2.columns:
                            valores = t13_grupo3_sprint2[col].unique()
                            print(f"   {col}: {valores}")
                    
                    # Verificar se agora aparece na análise
                    print(f"\n🎯 RESULTADO:")
                    print(f"   ✅ O Andre Eduardo (ID 2) agora aparece como avaliador")
                    print(f"   ✅ Suas avaliações da Sprint 2 foram incluídas")
                    print(f"   ✅ A análise.py agora deve contabilizar corretamente")
                else:
                    print("❌ ID 2 não tem registros da T13 Grupo 3 Sprint 2")
            else:
                print("❌ ID 2 ainda não está no consolidado como avaliador")
            
            # Verificar total de avaliadores da T13 Grupo 3 Sprint 2
            t13_grupo3_sprint2_todos = df[
                (df.get('turma') == 'T13') & 
                (df.get('time') == 'Grupo 3') & 
                (df.get('sprint') == 'Sprint 2')
            ]
            
            if not t13_grupo3_sprint2_todos.empty:
                avaliadores = t13_grupo3_sprint2_todos['id_avaliador'].unique()
                print(f"\n👥 Total de avaliadores T13 Grupo 3 Sprint 2: {len(avaliadores)}")
                print(f"👤 IDs dos avaliadores: {sorted(avaliadores)}")
                
                if 2 in avaliadores:
                    print("✅ ID 2 está entre os avaliadores!")
                else:
                    print("❌ ID 2 ainda não está entre os avaliadores")
        
        # Limpar arquivo temporário
        os.unlink(tmp.name)
        
    except Exception as e:
        print(f"❌ Erro ao verificar correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_correcao()
