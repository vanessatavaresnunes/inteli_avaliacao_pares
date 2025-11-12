import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

def calcular_k_por_tamanho_grupo(n: int) -> int:
    """
    Calcula o valor de K (lastro) baseado no tamanho do grupo N.
    
    Valores de K para o período 2025-2B:
    - N=4 → K=9
    - N=5 → K=14
    - N=6 → K=44
    - N=7 → K=54
    - N=8 → K=99
    
    Args:
        n: Tamanho do grupo (número de integrantes)
        
    Returns:
        Valor de K correspondente ao tamanho do grupo
    """
    k_map = {
        4: 9,
        5: 14,
        6: 44,
        7: 54,
        8: 99
    }
    return k_map.get(n, 54)  # Default para N=7 se não estiver no mapa

def calcular_indice_nova_formula(px: float, p_medio: float, p_max: float, p_min: float, n: int) -> float:
    """
    Calcula o índice usando a nova fórmula para o período 2025-2B:
    Índice = fator × (Px - Pmédi) / ((Pmax - Pmin) + K)
    Com limite entre -0.4 e +0.4
    
    Args:
        px: Pontos do aluno individual
        p_medio: Média dos pontos
        p_max: Máximo de pontos
        p_min: Mínimo de pontos
        n: Tamanho do grupo (para calcular K)
        
    Returns:
        Índice calculado (limitado entre -0.4 e +0.4)
    """
    fator = 7.5
    limite = 0.4
    k = calcular_k_por_tamanho_grupo(n)
    denominador = (p_max - p_min) + k
    if denominador == 0:
        return 0.0
    indice_calculado = fator * (px - p_medio) / denominador
    # Limitar entre -limite e +limite
    indice_limitado = max(-limite, min(limite, indice_calculado))
    return round(indice_limitado, 1)

def carregar_alunos_json(periodo: str = "2025-2A"):
    """
    Carrega dados dos alunos do arquivo alunos.json para um período específico
    
    Args:
        periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
    """
    try:
        with open('data/alunos.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            # Nova estrutura: {periodo: {T09: {...}, T13: {...}}}
            if periodo in dados and isinstance(dados[periodo], dict):
                return dados[periodo]
            return {}
    except Exception as e:
        print(f"Erro ao carregar alunos.json: {e}")
        return {}

st.set_page_config(page_title="Análise Local das Avaliações", layout="wide")

st.title("🔎 Análise Local das Avaliações de Pares")

# Função para processar todos os arquivos locais e criar cache
def processar_arquivos_locais():
    """Processa todos os arquivos JSON da pasta dados e cria arquivo de cache"""
    pasta_dados = Path("dados")
    
    if not pasta_dados.exists():
        st.error("Pasta 'dados' não encontrada! Execute o script baixar_todos_arquivos.py primeiro.")
        return None
    
    print("📂 Processando arquivos locais...")
    
    # Listar todos os arquivos JSON
    arquivos_json = list(pasta_dados.glob("aval_*.json"))
    print(f"📊 Total de arquivos encontrados: {len(arquivos_json)}")
    
    # Data de início da avaliação de pares da Sprint 5
    data_inicio_sprint5 = datetime(2025, 10, 6).timestamp()
    
    # Processar todos os arquivos
    todos_dados = []
    
    for i, arquivo in enumerate(arquivos_json):
        if (i + 1) % 50 == 0:
            print(f"   Processando arquivo {i+1}/{len(arquivos_json)}...")
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
            
            if conteudo:
                for linha in conteudo.splitlines():
                    linha = linha.strip()
                    if linha:
                        try:
                            dado = json.loads(linha)
                            if isinstance(dado, dict) and 'timestamp' in dado:
                                # Aplicar correção de Sprint 5
                                if 'sprint' in dado and dado['sprint'] == 'Sprint 4':
                                    timestamp = dado.get('timestamp', 0)
                                    if timestamp >= data_inicio_sprint5:
                                        dado['sprint'] = 'Sprint 5'
                                
                                todos_dados.append(dado)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"   ❌ Erro ao processar {arquivo.name}: {e}")
            continue
    
    if not todos_dados:
        print("❌ Nenhum dado encontrado nos arquivos locais")
        return None
    
    # Criar DataFrame
    df = pd.DataFrame(todos_dados)
    
    # Remover duplicatas
    print(f"📊 Total de registros antes da deduplicação: {len(df)}")
    df = df.drop_duplicates(
        subset=['timestamp', 'id_avaliador', 'id_avaliado', 'eixo'],
        keep='last'
    )
    print(f"📊 Total de registros após deduplicação: {len(df)}")
    
    # Salvar cache
    arquivo_cache = pasta_dados / "cache_avaliacoes.json"
    df.to_json(arquivo_cache, orient='records', lines=True, force_ascii=False)
    print(f"✅ Cache salvo em: {arquivo_cache}")
    
    return df

# Função para carregar dados do cache ou processar arquivos
def carregar_dados_locais(forcar_atualizacao=False):
    """Carrega dados do cache ou processa arquivos se necessário"""
    pasta_dados = Path("dados")
    arquivo_cache = pasta_dados / "cache_avaliacoes.json"
    
    # Se forçar atualização ou não existir cache, processar arquivos
    if forcar_atualizacao or not arquivo_cache.exists():
        return processar_arquivos_locais()
    
    # Carregar do cache
    try:
        df = pd.read_json(arquivo_cache, lines=True)
        return df
    except Exception as e:
        st.warning(f"Erro ao carregar cache: {e}. Processando arquivos...")
        return processar_arquivos_locais()

# Botão para atualizar dados
if st.button("🔄 Atualizar Dados dos Arquivos Locais"):
    with st.spinner("Processando todos os arquivos da pasta 'dados'..."):
        df = carregar_dados_locais(forcar_atualizacao=True)
        if df is not None and not df.empty:
            st.session_state.df_local = df
            st.success(f"✅ Dados atualizados! Total de {len(df)} registros processados.")
            st.rerun()
        else:
            st.error("❌ Erro ao processar arquivos locais")

# Carregar dados
if 'df_local' not in st.session_state:
    with st.spinner("Carregando dados do cache..."):
        st.session_state.df_local = carregar_dados_locais()

df = st.session_state.df_local

if df is None or df.empty:
    st.warning("Nenhum dado encontrado. Execute o script baixar_todos_arquivos.py primeiro para baixar os arquivos do Supabase.")
    st.stop()

st.success(f"✅ {len(df)} registros carregados")

# Mostrar estatísticas gerais
turmas_disponiveis = sorted(df['turma'].unique())
st.info(f"📊 Turmas disponíveis: {', '.join(turmas_disponiveis)}")

# Carregar todas as turmas disponíveis (não apenas as com avaliações)
def carregar_todas_turmas(df_avaliacoes):
    """Carrega todas as turmas disponíveis de diferentes fontes"""
    turmas_avaliacao = []
    turmas_alunos = []
    
    # 1. Turmas com dados de avaliação
    if df_avaliacoes is not None and not df_avaliacoes.empty and 'turma' in df_avaliacoes.columns:
        turmas_validas = df_avaliacoes['turma'].dropna()
        turmas_validas = turmas_validas[turmas_validas != '']
        turmas_avaliacao = sorted(turmas_validas.unique())
    
    # 2. Turmas do arquivo de alunos (definição oficial)
    alunos_data = carregar_alunos_json()
    turmas_alunos = sorted(list(alunos_data.keys()))
    
    # Combinar todas as turmas
    todas_turmas = sorted(set(turmas_alunos + turmas_avaliacao))
    return todas_turmas

# Carregar todas as turmas disponíveis
todas_turmas = carregar_todas_turmas(df)

if not todas_turmas:
    st.error("Nenhuma turma encontrada nos arquivos de configuração.")
    st.stop()

# Seleção de turma
turma_selecionada = st.selectbox("Selecione a turma para análise:", todas_turmas, key="analise_turma")

# Filtrar dados da turma selecionada
df_turma = df[df['turma'] == turma_selecionada].copy() if not df.empty and 'turma' in df.columns else pd.DataFrame()

# Verificar se há dados de avaliação para esta turma
tem_avaliacoes = not df_turma.empty

# Informações da turma selecionada
st.info(f"📊 **Turma Selecionada:** {turma_selecionada}")

# Estatísticas gerais
col1, col2 = st.columns(2)

# Contar grupos do arquivo de alunos
grupos_count = 0
alunos_data = carregar_alunos_json()
if turma_selecionada in alunos_data:
    grupos_count = len(alunos_data[turma_selecionada])

with col1:
    st.metric("Grupos", grupos_count)

# Contar alunos que avaliaram vs total de alunos
with col2:
    if tem_avaliacoes:
        alunos_que_avaliaram = len(df_turma["id_avaliador"].unique())
        total_alunos = 0
        try:
            with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
            for email, dados in usuarios.items():
                if dados.get('turma') == turma_selecionada:
                    total_alunos += 1
        except:
            pass
        st.metric("Alunos que Avaliaram", f"{alunos_que_avaliaram} / {total_alunos}")
    else:
        total_alunos = 0
        try:
            with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
            for email, dados in usuarios.items():
                if dados.get('turma') == turma_selecionada:
                    total_alunos += 1
        except:
            pass
        st.metric("Alunos que Avaliaram", f"0 / {total_alunos}")

# Carregar todos os grupos da turma
def carregar_todos_grupos_turma(turma):
    """Carrega todos os grupos de uma turma"""
    grupos_avaliacao = sorted(df_turma["time"].unique()) if not df_turma.empty else []
    
    # Carregar do arquivo de alunos
    alunos_data = carregar_alunos_json()
    grupos_alunos = []
    if turma in alunos_data:
        grupos_alunos = sorted(list(alunos_data[turma].keys()))
    
    # Combinar todos os grupos
    todos_grupos = sorted(set(grupos_alunos + grupos_avaliacao))
    return todos_grupos

grupos = carregar_todos_grupos_turma(turma_selecionada)
sprints = sorted(df_turma["sprint"].unique()) if not df_turma.empty else []

if not grupos:
    st.warning(f"Nenhum grupo encontrado para a turma {turma_selecionada}.")
    st.stop()

# Análise por grupo e sprint
st.header("📈 Análise por Grupo e Sprint")

if not tem_avaliacoes:
    st.info(f"ℹ️ **Turma {turma_selecionada}**: Nenhuma avaliação foi realizada ainda.")
    st.stop()

for grupo in grupos:
    with st.expander(f"🏢 Grupo: {grupo}", expanded=False):
        df_grupo = df_turma[df_turma["time"] == grupo]
        
        if df_grupo.empty:
            st.info("📝 Nenhuma avaliação realizada ainda neste grupo.")
            continue
        
        for sprint in sprints:
            df_sprint = df_grupo[df_grupo["sprint"] == sprint]

            if df_sprint.empty:
                continue
                
            # Manter apenas a última avaliação de cada avaliador para cada avaliado/eixo
            df_sprint_sorted = df_sprint.sort_values("timestamp")
            df_sprint_last = df_sprint_sorted.groupby([
                "id_avaliador", "id_avaliado", "eixo"
            ], as_index=False).last()
            
            st.subheader(f"🚀 Sprint: {sprint}")
            
            # Pegar TODOS os alunos do grupo
            alunos_avaliados = set(df_sprint_last["nome_avaliado"].unique())
            alunos_avaliadores = set(df_sprint_last["nome_avaliador"].unique())
            
            # Filtrar valores None
            alunos_avaliados_filtrado = {aluno for aluno in alunos_avaliados if aluno is not None}
            alunos_avaliadores_filtrado = {aluno for aluno in alunos_avaliadores if aluno is not None}
            todos_alunos_sprint = sorted(alunos_avaliados_filtrado.union(alunos_avaliadores_filtrado))
            
            eixos = sorted(df_sprint_last["eixo"].unique())
            alunos = todos_alunos_sprint
            
            # Montar tabela de somatórios
            dados = []
            n_avaliadores = len(df_sprint_last["id_avaliador"].unique())
            
            for aluno in alunos:
                linha = {}
                completo = True
                
                for eixo in eixos:
                    avals = df_sprint_last[(df_sprint_last["nome_avaliado"] == aluno) & (df_sprint_last["eixo"] == eixo)]
                    soma = avals["nota"].sum()
                    linha[eixo] = soma
                    n_recebidas = len(avals)
                    if n_recebidas < n_avaliadores - 1:
                        completo = False
                
                # Verificar se o aluno fez avaliações
                fez_avaliacao = aluno in df_sprint_last["nome_avaliador"].unique()
                
                if not fez_avaliacao:
                    aluno_ids_avaliado = df_sprint_last[df_sprint_last["nome_avaliado"] == aluno]["id_avaliado"].unique()
                    aluno_ids_avaliador = df_sprint_last[df_sprint_last["nome_avaliador"] == aluno]["id_avaliador"].unique()
                    aluno_ids = list(aluno_ids_avaliado) + list(aluno_ids_avaliador)
                    
                    if len(aluno_ids) > 0:
                        aluno_id = aluno_ids[0]
                        fez_avaliacao = aluno_id in df_sprint_last["id_avaliador"].unique()
                
                if not fez_avaliacao:
                    completo = False
                
                linha["Total"] = sum(linha[eixo] for eixo in eixos)
                
                # Nome colorido conforme status
                if completo:
                    linha["Aluno"] = f'<span style="color:green;font-weight:bold">{aluno}</span>'
                else:
                    linha["Aluno"] = f'<span style="color:red;font-weight:bold">{aluno}</span>'
                
                dados.append(linha)
            
            if not dados:
                st.warning("Nenhum dado encontrado para esta sprint.")
                continue
            
            # Criar DataFrame de resultados
            ordem_eixos = ["Entregas reais", "Valor Percebido", "Caixa de Ferramentas"]
            colunas_ordenadas = ["Aluno"] + [eixo for eixo in ordem_eixos if eixo in dados[0]] + ["Total", "Nota"]
            df_result = pd.DataFrame(dados)
            
            # Adicionar coluna Nota
            if "Nota" not in df_result.columns:
                df_result["Nota"] = ""
            df_result = df_result[colunas_ordenadas]
            df_result = df_result.sort_values("Aluno")
            
            # Calcular a nota conforme fórmula fornecida (1 casa decimal)
            if not df_result.empty:
                medias = df_result["Total"].mean()
                maior = df_result["Total"].max()
                menor = df_result["Total"].min()
                n_alunos = len(df_result)  # Tamanho do grupo (N)
                
                # Verificar período atual via variável de ambiente
                periodo_atual = os.getenv("PERIODO_ATUAL", "2025-2A")
                
                # Usar nova fórmula para período 2025-2B, fórmula antiga para outros períodos
                if periodo_atual == "2025-2B":
                    # Nova fórmula: Índice = (Px - Pmédi) / ((Pmax - Pmin) + K)
                    df_result["Nota"] = df_result["Total"].apply(
                        lambda px: calcular_indice_nova_formula(px, medias, maior, menor, n_alunos)
                    )
                else:
                    # Fórmula antiga: (Total - Média) / (0.6 × Amplitude)
                    denominador = 0.6 * (maior - menor) if maior != menor else 1
                    df_result["Nota"] = ((df_result["Total"] - medias) / denominador).round(1)
            
            # Exibir tabela
            st.markdown(
                df_result.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

# Exibir feedbacks
st.header("💬 Feedbacks Recebidos por Aluno")

with st.expander("📋 Tabela de Feedbacks", expanded=False):
    feedback_data = []
    
    for grupo in grupos:
        df_grupo = df_turma[df_turma["time"] == grupo]
        for sprint in sprints:
            df_sprint = df_grupo[df_grupo["sprint"] == sprint]
            if df_sprint.empty:
                continue
            df_sprint_sorted = df_sprint.sort_values("timestamp")
            df_sprint_last = df_sprint_sorted.groupby([
                "id_avaliador", "id_avaliado", "eixo"
            ], as_index=False).last()
            alunos = sorted([aluno for aluno in df_sprint_last["nome_avaliado"].unique() if aluno is not None])
            for aluno in alunos:
                linha = {"Aluno": aluno, "Grupo": grupo, "Sprint": sprint}
                for eixo in ["Entregas reais", "Valor Percebido", "Caixa de Ferramentas"]:
                    feedbacks = df_sprint_last[(df_sprint_last["nome_avaliado"] == aluno) & (df_sprint_last["eixo"].str.lower().str.contains(eixo.lower()))]["feedback"].dropna().tolist()
                    linha[eixo] = '\n'.join(f'- {fb}' for fb in feedbacks) if feedbacks else ""
                feedback_data.append(linha)
    
    if not feedback_data:
        st.warning("Nenhum feedback encontrado.")
    else:
        df_feedback = pd.DataFrame(feedback_data)
        colunas = ["Grupo", "Sprint", "Aluno", "Entregas reais", "Valor Percebido", "Caixa de Ferramentas"]
        df_feedback = df_feedback[colunas]

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            grupos_unicos = sorted(df_feedback["Grupo"].unique())
            grupo_sel = st.selectbox("Filtrar por grupo:", options=["Todos"] + grupos_unicos, index=0, key="feedback_grupo")
        with col2:
            sprints_unicos = sorted(df_feedback["Sprint"].unique())
            sprint_sel = st.selectbox("Filtrar por sprint:", options=["Todos"] + sprints_unicos, index=0, key="feedback_sprint")

        df_filtrado = df_feedback.copy()
        if grupo_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Grupo"] == grupo_sel]
        if sprint_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Sprint"] == sprint_sel]

        df_filtrado = df_filtrado.sort_values("Aluno")

        def format_cell(text):
            if not text:
                return ""
            return '<br>'.join(text.split('\n'))

        html = '<table border="1" style="border-collapse:collapse;width:100%">'
        html += '<tr>' + ''.join(f'<th>{col}</th>' for col in df_filtrado.columns) + '</tr>'
        for _, row in df_filtrado.iterrows():
            html += '<tr>' + ''.join(f'<td>{format_cell(str(row[col]))}</td>' for col in df_filtrado.columns) + '</tr>'
        html += '</table>'
        st.markdown(html, unsafe_allow_html=True)


