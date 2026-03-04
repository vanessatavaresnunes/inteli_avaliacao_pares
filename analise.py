import streamlit as st
import pandas as pd
from src.utils.supabase_storage import download_json_from_bucket, get_bucket_for_period
import json
import tempfile
import os

def calcular_k_por_tamanho_grupo(n: int) -> int:
    """
    Calcula o valor de K (lastro) baseado no tamanho do grupo N.
    
    Valores de K baseados no tamanho do grupo N:
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
    Calcula o índice usando a nova fórmula:
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
        periodo: Período acadêmico (ex: "2026-1A")
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

def carregar_sprint_dates(periodo: str = "2026-1A"):
    """
    Carrega datas das sprints para o período
    """
    try:
        arquivo = 'data/sprint_dates_2026_1a.json'
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f).get("sprints", {})
    except Exception as e:
        print(f"Erro ao carregar sprint_dates: {e}")
        return {}

st.set_page_config(page_title="Análise das Avaliações", layout="wide")

st.title("🔎 Análise das Avaliações de Pares")

# Período fixo
periodo_atual = "2026-1A"

st.markdown("---")

# Botões de ação
col1, col2 = st.columns(2)

with col1:
    # Botão para forçar a recarga dos dados
    if st.button("🔄 Recarregar Dados do Consolidado"):
        with st.spinner(f"Forçando a recriação do arquivo consolidado a partir de todos os dados do bucket de {periodo_atual}..."):
            try:
                from src.models.avaliacao import AvaliacaoModel
                avaliacao_model = AvaliacaoModel()
                sucesso = avaliacao_model.regenerar_consolidado_de_todos_os_arquivos(periodo=periodo_atual)
                if sucesso:
                    st.success("✅ Arquivo consolidado recriado com sucesso!")
                    st.rerun()  # Recarregar a página para mostrar os novos dados
                else:
                    st.error("❌ Erro ao recarregar os dados")
            except Exception as e:
                st.error(f"❌ Erro ao recarregar os dados: {e}")

with col2:
    # Botão para busca direta (contorna limitação de 100 arquivos)
    if st.button("🎯 Busca Direta por Turma/Sprint"):
        st.session_state.show_direct_search = True
        st.rerun()

# Interface de busca direta
if st.session_state.get('show_direct_search', False):
    st.markdown("---")
    st.subheader("🎯 Busca Direta no Supabase")
    st.info("Esta busca contorna a limitação de 100 arquivos, buscando diretamente por turma e sprint no Supabase.")
    
    col_turma, col_sprint, col_buscar = st.columns([2, 2, 1])
    
    with col_turma:
        turma_busca = st.selectbox(
            "Turma:",
            options=["T17", "Teste"],
            key="turma_busca_direta"
        )
    
    with col_sprint:
        sprint_busca = st.selectbox(
            "Sprint:",
            options=["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5"],
            key="sprint_busca_direta"
        )
    
    with col_buscar:
        st.write("")  # Espaçamento
        if st.button("🔍 Buscar", type="primary"):
            with st.spinner(f"Buscando dados de {turma_busca} - {sprint_busca}..."):
                try:
                    from src.utils.busca_direta_supabase import buscar_avaliacoes_por_turma_sprint
                    
                    df_busca = buscar_avaliacoes_por_turma_sprint(turma_busca, sprint_busca, periodo=periodo_atual)
                    
                    if not df_busca.empty:
                        st.success(f"✅ Encontrados {len(df_busca)} registros para {turma_busca} - {sprint_busca}")
                        
                        # Atualizar o dataframe principal com os dados encontrados
                        st.session_state.df_busca_direta = df_busca
                        st.session_state.turma_busca_atual = turma_busca
                        st.session_state.sprint_busca_atual = sprint_busca
                        st.rerun()
                    else:
                        st.warning(f"❌ Nenhum dado encontrado para {turma_busca} - {sprint_busca}")
                        
                except Exception as e:
                    st.error(f"❌ Erro na busca: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    if st.button("❌ Fechar Busca Direta"):
        st.session_state.show_direct_search = False
        if 'df_busca_direta' in st.session_state:
            del st.session_state.df_busca_direta
        if 'turma_busca_atual' in st.session_state:
            del st.session_state.turma_busca_atual
        if 'sprint_busca_atual' in st.session_state:
            del st.session_state.sprint_busca_atual
        st.rerun()
    
    st.markdown("---")

# Se houver dados de busca direta, usar eles ao invés do arquivo consolidado
if 'df_busca_direta' in st.session_state and not st.session_state.df_busca_direta.empty:
    df = st.session_state.df_busca_direta
    st.info(f"📊 Exibindo dados de busca direta: {st.session_state.turma_busca_atual} - {st.session_state.sprint_busca_atual}")

# Carregar dados do arquivo consolidado
def carregar_dados_consolidados(periodo: str = "2025-2A"):
    """Carrega dados do arquivo consolidado do Supabase
    
    Args:
        periodo: Período acadêmico (ex: "2025-2A", "2025-2B")
    """
    try:
        # Determinar bucket baseado no período
        bucket_name = get_bucket_for_period(periodo)
        st.info(f"📦 Carregando dados do bucket: {bucket_name}")
        
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
            
            return pd.DataFrame(linhas)
    except Exception as e:
        st.error(f"Erro ao carregar dados consolidados: {str(e)}")
        return pd.DataFrame()
    finally:
        try:
            os.unlink(tmp.name)
        except:
            pass

# Carregar dados
df = carregar_dados_consolidados(periodo_atual)

if df.empty:
    st.warning("Nenhum dado de avaliação encontrado no Supabase.")
    st.stop()

# Verificar presença de T13 (sem alerta de limitação; paginação já implementada)
turmas_no_df = df['turma'].unique() if not df.empty else []

# Carregar todas as turmas disponíveis (não apenas as com avaliações)
def carregar_todas_turmas(df_avaliacoes):
    """Carrega apenas as turmas configuradas para o período atual no alunos.json"""
    alunos_data = carregar_alunos_json(periodo_atual)
    turmas = sorted(list(alunos_data.keys())) if alunos_data else ["T17"]
    return turmas

# Carregar todas as turmas disponíveis
todas_turmas = carregar_todas_turmas(df)

if not todas_turmas:
    st.error("Nenhuma turma encontrada nos arquivos de configuração.")
    st.stop()

# Seleção de turma
turma_selecionada = st.selectbox("Selecione a turma para análise:", todas_turmas, key="analise_turma")

# Filtrar dados da turma selecionada (se houver dados de avaliação)
df_turma = df[df['turma'] == turma_selecionada].copy() if not df.empty and 'turma' in df.columns else pd.DataFrame()

# Lógica para limpar timestamps inválidos e corrigir a Sprint 5
if not df_turma.empty:
    # PASSO 1: Normalizar timestamps (segundos e milissegundos)
    df_turma['timestamp_numeric'] = pd.to_numeric(df_turma['timestamp'], errors='coerce')
    
    # Identifica timestamps em milissegundos (números muito grandes) e os converte para segundos
    is_milliseconds = df_turma['timestamp_numeric'] > 10**12
    df_turma.loc[is_milliseconds, 'timestamp_numeric'] = df_turma.loc[is_milliseconds, 'timestamp_numeric'] / 1000
    
    # Converte para datetime, agora que todos estão em segundos
    df_turma['timestamp_dt'] = pd.to_datetime(df_turma['timestamp_numeric'], unit='s', errors='coerce')
    
    erros_de_data = df_turma['timestamp_dt'].isnull().sum()
    if erros_de_data > 0:
        st.warning(f"{erros_de_data} avaliações com timestamp inválido foram ignoradas na análise.")
        df_turma.dropna(subset=['timestamp_dt'], inplace=True)

    # PASSO 2: Aplicar a regra da Sprint 5 aos dados limpos
    try:
        sprints_info = carregar_sprint_dates(periodo_atual)
        
        sprint_5_info = sprints_info.get("sprint_5", {})
        if "data_avalpares_inicio" in sprint_5_info:
            data_inicio_s5 = pd.to_datetime(sprint_5_info["data_avalpares_inicio"])
            filtro_data = df_turma['timestamp_dt'] >= data_inicio_s5
            df_turma.loc[filtro_data, 'sprint'] = 'Sprint 5'

    except Exception as e:
        st.warning(f"Não foi possível aplicar a regra de data para a Sprint 5: {e}")

# Verificar se há dados de avaliação para esta turma
tem_avaliacoes = not df_turma.empty

# Verificar se há dados de avaliação para esta turma
if tem_avaliacoes:
    # Garantir colunas essenciais apenas se há dados de avaliação
    for col in ["time", "sprint", "nome_avaliado", "eixo", "nota"]:
        if col not in df_turma.columns:
            st.error(f"Coluna obrigatória ausente: {col}")
            st.stop()

# Informações da turma selecionada
st.info(f"📊 **Turma Selecionada:** {turma_selecionada}")

# Estatísticas gerais
col1, col2 = st.columns(2)

# Contar grupos do arquivo de alunos (sempre usar a fonte oficial)
grupos_count = 0
alunos_data = carregar_alunos_json(periodo_atual)
if turma_selecionada in alunos_data:
    grupos_count = len(alunos_data[turma_selecionada])

with col1:
    st.metric("Grupos", grupos_count)

# Contar alunos que avaliaram vs total de alunos
with col2:
    if tem_avaliacoes:
        # Alunos que fizeram avaliações (como avaliadores)
        alunos_que_avaliaram = len(df_turma["id_avaliador"].unique())
        
        # Total de alunos da turma
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
        # Sem avaliações, mostrar 0 / total
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
    
    # Tentar carregar do arquivo de alunos (definição oficial dos grupos)
    alunos_data = carregar_alunos_json(periodo_atual)
    grupos_alunos = []
    if turma in alunos_data:
        grupos_alunos = sorted(list(alunos_data[turma].keys()))
    
    # Tentar carregar do arquivo de usuários (fallback)
    grupos_usuarios = []
    try:
        with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        
        grupos_set = set()
        for email, dados in usuarios.items():
            if dados.get('turma') == turma and 'time' in dados:
                grupos_set.add(dados['time'])
        
        grupos_usuarios = sorted(list(grupos_set))
    except Exception as e:
        print(f"Erro ao carregar grupos do arquivo de usuários: {e}")
    
    # Combinar todos os grupos (prioridade: alunos.json > usuarios.json > avaliações)
    todos_grupos = sorted(set(grupos_alunos + grupos_usuarios + grupos_avaliacao))
    return todos_grupos

grupos = carregar_todos_grupos_turma(turma_selecionada)
sprints = sorted(df_turma["sprint"].unique()) if not df_turma.empty else []

# Se não há grupos, mostrar mensagem
if not grupos:
    st.warning(f"Nenhum grupo encontrado para a turma {turma_selecionada}.")
    st.stop()

# Análise por grupo e sprint
st.header("📈 Análise por Grupo e Sprint")

# Mostrar mensagem se não há avaliações para esta turma
if not tem_avaliacoes:
    st.info(f"ℹ️ **Turma {turma_selecionada}**: Nenhuma avaliação foi realizada ainda. Os grupos e alunos são mostrados com base na configuração oficial.")
    st.markdown("---")

# Carregar datas das sprints para filtro especial da Sprint 5
sprint_dates = carregar_sprint_dates(periodo_atual)

for grupo in grupos:
    with st.expander(f"🏢 Grupo: {grupo}", expanded=False):
        df_grupo = df_turma[df_turma["time"] == grupo] if not df_turma.empty else pd.DataFrame()
        
        # Carregar alunos do grupo
        def carregar_alunos_grupo(turma, grupo):
            """Carrega todos os alunos de um grupo específico"""
            alunos = []
            
            # Primeiro tentar carregar do arquivo de alunos (definição oficial)
            alunos_data = carregar_alunos_json(periodo_atual)
            
            if turma in alunos_data and grupo in alunos_data[turma]:
                # Pegar IDs dos alunos do grupo
                ids_alunos = alunos_data[turma][grupo]
                
                # Buscar nomes dos alunos no arquivo de usuários
                with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
                    usuarios = json.load(f)
                
                for email, dados in usuarios.items():
                    if dados.get('turma') == turma and dados.get('id') in ids_alunos:
                        alunos.append(dados.get('name', email))
            
            # Fallback: tentar carregar do arquivo de usuários diretamente
            if not alunos:
                try:
                    with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
                        usuarios = json.load(f)
                    
                    for email, dados in usuarios.items():
                        if dados.get('turma') == turma and dados.get('time') == grupo:
                            alunos.append(dados.get('name', email))
                            
                except Exception as e:
                    print(f"Erro ao carregar alunos do grupo via usuarios.json: {e}")
            
            return sorted(alunos)
        
        # Pegar TODOS os alunos do grupo (tanto avaliados quanto avaliadores) de todas as sprints
        todos_alunos_avaliados = set()
        todos_alunos_avaliadores = set()
        
        if not df_grupo.empty:
            for sprint in sprints:
                df_sprint = df_grupo[df_grupo["sprint"] == sprint]
                if not df_sprint.empty:
                    todos_alunos_avaliados.update(df_sprint["nome_avaliado"].unique())
                    todos_alunos_avaliadores.update(df_sprint["nome_avaliador"].unique())
        
        # Combinar alunos dos dados de avaliação com alunos do arquivo de usuários
        alunos_avaliacao = todos_alunos_avaliados.union(todos_alunos_avaliadores)
        alunos_usuarios = set(carregar_alunos_grupo(turma_selecionada, grupo))
        
        # Filtrar valores None antes da ordenação
        alunos_avaliacao_filtrado = {aluno for aluno in alunos_avaliacao if aluno is not None}
        todos_alunos = sorted(alunos_avaliacao_filtrado.union(alunos_usuarios))
        
        # Estatísticas do grupo
        st.metric("Alunos no Grupo", len(todos_alunos))
        
        # Verificar se há dados de avaliação para este grupo
        if df_grupo.empty:
            st.info("📝 Nenhuma avaliação realizada ainda neste grupo.")
            # Mostrar lista de alunos do grupo em vermelho (não fizeram avaliação)
            if todos_alunos:
                st.write("**Alunos do grupo:**")
                for aluno in todos_alunos:
                    st.markdown(f'<span style="color:red;font-weight:bold">• {aluno}</span>', unsafe_allow_html=True)
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
            
            # Pegar TODOS os alunos do grupo (tanto avaliados quanto avaliadores)
            alunos_avaliados = set(df_sprint_last["nome_avaliado"].unique())
            alunos_avaliadores = set(df_sprint_last["nome_avaliador"].unique())
            
            # Filtrar valores None antes da ordenação
            alunos_avaliados_filtrado = {aluno for aluno in alunos_avaliados if aluno is not None}
            alunos_avaliadores_filtrado = {aluno for aluno in alunos_avaliadores if aluno is not None}
            todos_alunos_sprint = sorted(alunos_avaliados_filtrado.union(alunos_avaliadores_filtrado))
            
            eixos = sorted(df_sprint_last["eixo"].unique())
            
            print(f"  - Alunos avaliados: {sorted(alunos_avaliados_filtrado)}")
            print(f"  - Alunos avaliadores: {sorted(alunos_avaliadores_filtrado)}")
            print(f"  - Todos os alunos: {todos_alunos_sprint}")
            
            alunos = todos_alunos_sprint
            
            # Montar tabela de somatórios e checar status de avaliações
            dados = []
            n_avaliadores = len(df_sprint_last["id_avaliador"].unique())
            
            # Debug: verificar dados disponíveis
            print(f"🔍 DEBUG - Grupo: {grupo}, Sprint: {sprint}")
            print(f"  - Alunos avaliados: {sorted([aluno for aluno in df_sprint_last['nome_avaliado'].unique() if aluno is not None])}")
            print(f"  - Avaliadores (nomes): {sorted([aluno for aluno in df_sprint_last['nome_avaliador'].unique() if aluno is not None])}")
            print(f"  - Avaliadores (IDs): {sorted(df_sprint_last['id_avaliador'].unique())}")
            print(f"  - Total de avaliadores: {n_avaliadores}")
            
            for aluno in alunos:
                linha = {}
                # Checar se o aluno recebeu todas as avaliações esperadas (por eixo)
                completo = True
                
                for eixo in eixos:
                    avals = df_sprint_last[(df_sprint_last["nome_avaliado"] == aluno) & (df_sprint_last["eixo"] == eixo)]
                    soma = avals["nota"].sum()
                    linha[eixo] = soma
                    # Esperado: 1 avaliação de cada avaliador (exceto autoavaliação)
                    n_recebidas = len(avals)
                    if n_recebidas < n_avaliadores - 1:
                        completo = False
                
                # Checar se o aluno fez avaliações (como avaliador)
                # Primeiro tentar buscar pelo nome
                fez_avaliacao = aluno in df_sprint_last["nome_avaliador"].unique()
                
                # Se não encontrou pelo nome, tentar buscar pelo ID
                if not fez_avaliacao:
                    # Buscar o ID do aluno (pode estar como avaliado ou avaliador)
                    aluno_ids_avaliado = df_sprint_last[df_sprint_last["nome_avaliado"] == aluno]["id_avaliado"].unique()
                    aluno_ids_avaliador = df_sprint_last[df_sprint_last["nome_avaliador"] == aluno]["id_avaliador"].unique()
                    
                    # Pegar qualquer ID encontrado
                    aluno_ids = list(aluno_ids_avaliado) + list(aluno_ids_avaliador)
                    
                    if len(aluno_ids) > 0:
                        aluno_id = aluno_ids[0]  # Pegar o primeiro ID encontrado
                        # Verificar se este ID aparece como avaliador (quem fez avaliações)
                        fez_avaliacao = aluno_id in df_sprint_last["id_avaliador"].unique()
                
                print(f"  - Aluno: {aluno}")
                print(f"    - Fez avaliação (nome): {aluno in df_sprint_last['nome_avaliador'].unique()}")
                print(f"    - Fez avaliação (ID): {fez_avaliacao}")
                print(f"    - Completo antes: {completo}")
                
                if not fez_avaliacao:
                    completo = False
                
                print(f"    - Completo depois: {completo}")
                
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
            
            # Garantir ordem das colunas: Aluno, Entregas Reais, Valor Percebido, Caixa de Ferramentas, Total, Nota
            ordem_eixos = ["Entregas reais", "Valor Percebido", "Caixa de Ferramentas"]
            colunas_ordenadas = ["Aluno"] + [eixo for eixo in ordem_eixos if eixo in dados[0]] + ["Total", "Nota"]
            df_result = pd.DataFrame(dados)
            
            # Adiciona coluna Nota se não existir ainda (antes do cálculo)
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
                
                # Sempre usar a nova fórmula para 2026-1A em diante
                # Nova fórmula: Índice = (Px - Pmédi) / ((Pmax - Pmin) + K)
                df_result["Nota"] = df_result["Total"].apply(
                    lambda px: calcular_indice_nova_formula(px, medias, maior, menor, n_alunos)
                )
            
            # Exibir tabela com nomes coloridos
            st.markdown(
                df_result.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

# Exibir feedbacks recebidos por cada aluno em tabela colapsável
st.header("💬 Feedbacks Recebidos por Aluno")

with st.expander("📋 Tabela de Feedbacks", expanded=False):
    feedback_data = []
    # Para todos os grupos e sprints da turma selecionada
    for grupo in grupos:
        df_grupo = df_turma[df_turma["time"] == grupo] if not df_turma.empty else pd.DataFrame()
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
        st.warning("Nenhum feedback encontrado para esta turma.")
    else:
        df_feedback = pd.DataFrame(feedback_data)
        # Garante ordem das colunas: Grupo, Sprint, Aluno, Entregas reais, Valor Percebido, Caixa de Ferramentas
        colunas = ["Grupo", "Sprint", "Aluno", "Entregas reais", "Valor Percebido", "Caixa de Ferramentas"]
        df_feedback = df_feedback[colunas]

        # Filtros de grupo e sprint
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

        # Ordenar por nome do aluno
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
