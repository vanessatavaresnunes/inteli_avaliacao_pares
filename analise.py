import streamlit as st
import pandas as pd
from src.utils.supabase_storage import download_json_from_bucket
import json
import tempfile
import os

st.set_page_config(page_title="Análise das Avaliações", layout="wide")

st.title("🔎 Análise das Avaliações de Pares")

# Carregar dados do arquivo consolidado
def carregar_dados_consolidados():
    """Carrega dados do arquivo consolidado do Supabase"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as tmp:
            download_json_from_bucket('avaliacoescompletas_consolidadas.json', tmp.name)
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
df = carregar_dados_consolidados()

if df.empty:
    st.warning("Nenhum dado de avaliação encontrado no Supabase.")
    st.stop()

# Carregar todas as turmas disponíveis (não apenas as com avaliações)
def carregar_todas_turmas(df_avaliacoes):
    """Carrega todas as turmas disponíveis de diferentes fontes"""
    turmas_avaliacao = []
    turmas_alunos = []
    turmas_usuarios = []
    
    # 1. Turmas com dados de avaliação
    if not df_avaliacoes.empty and 'turma' in df_avaliacoes.columns:
        turmas_avaliacao = sorted(df_avaliacoes['turma'].unique())
    
    # 2. Turmas do arquivo de alunos (definição oficial)
    try:
        with open('data/alunos.json', 'r', encoding='utf-8') as f:
            alunos_data = json.load(f)
        turmas_alunos = sorted(list(alunos_data.keys()))
    except Exception as e:
        print(f"Erro ao carregar turmas do arquivo de alunos: {e}")
    
    # 3. Turmas do arquivo de usuários (fallback)
    try:
        with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        
        turmas_set = set()
        for email, dados in usuarios.items():
            if 'turma' in dados:
                turmas_set.add(dados['turma'])
        turmas_usuarios = sorted(list(turmas_set))
    except Exception as e:
        print(f"Erro ao carregar turmas do arquivo de usuários: {e}")
    
    # Combinar todas as turmas (prioridade: alunos.json > usuarios.json > avaliações)
    todas_turmas = sorted(set(turmas_alunos + turmas_usuarios + turmas_avaliacao))
    return todas_turmas

# Carregar todas as turmas disponíveis
todas_turmas = carregar_todas_turmas(df)

if not todas_turmas:
    st.error("Nenhuma turma encontrada nos arquivos de configuração.")
    st.stop()

# Seleção de turma
turma_selecionada = st.selectbox("Selecione a turma para análise:", todas_turmas, key="analise_turma")

# Filtrar dados da turma selecionada (se houver dados de avaliação)
df_turma = df[df['turma'] == turma_selecionada] if not df.empty and 'turma' in df.columns else pd.DataFrame()

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
try:
    with open('data/alunos.json', 'r', encoding='utf-8') as f:
        alunos_data = json.load(f)
    if turma_selecionada in alunos_data:
        grupos_count = len(alunos_data[turma_selecionada])
except:
    pass

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
    grupos_alunos = []
    try:
        with open('data/alunos.json', 'r', encoding='utf-8') as f:
            alunos_data = json.load(f)
        
        if turma in alunos_data:
            grupos_alunos = sorted(list(alunos_data[turma].keys()))
    except Exception as e:
        print(f"Erro ao carregar grupos do arquivo de alunos: {e}")
    
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

for grupo in grupos:
    with st.expander(f"🏢 Grupo: {grupo}", expanded=False):
        df_grupo = df_turma[df_turma["time"] == grupo] if not df_turma.empty else pd.DataFrame()
        
        # Carregar alunos do grupo
        def carregar_alunos_grupo(turma, grupo):
            """Carrega todos os alunos de um grupo específico"""
            alunos = []
            
            # Primeiro tentar carregar do arquivo de alunos (definição oficial)
            try:
                with open('data/alunos.json', 'r', encoding='utf-8') as f:
                    alunos_data = json.load(f)
                
                if turma in alunos_data and grupo in alunos_data[turma]:
                    # Pegar IDs dos alunos do grupo
                    ids_alunos = alunos_data[turma][grupo]
                    
                    # Buscar nomes dos alunos no arquivo de usuários
                    with open('data/usuarios/usuarios.json', 'r', encoding='utf-8') as f:
                        usuarios = json.load(f)
                    
                    for email, dados in usuarios.items():
                        if dados.get('turma') == turma and dados.get('id') in ids_alunos:
                            alunos.append(dados.get('name', email))
                            
            except Exception as e:
                print(f"Erro ao carregar alunos do grupo via alunos.json: {e}")
            
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
        todos_alunos = sorted(alunos_avaliacao.union(alunos_usuarios))
        
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
            todos_alunos_sprint = sorted(alunos_avaliados.union(alunos_avaliadores))
            
            eixos = sorted(df_sprint_last["eixo"].unique())
            
            print(f"  - Alunos avaliados: {sorted(alunos_avaliados)}")
            print(f"  - Alunos avaliadores: {sorted(alunos_avaliadores)}")
            print(f"  - Todos os alunos: {todos_alunos_sprint}")
            
            alunos = todos_alunos_sprint
            
            # Montar tabela de somatórios e checar status de avaliações
            dados = []
            n_avaliadores = len(df_sprint_last["id_avaliador"].unique())
            
            # Debug: verificar dados disponíveis
            print(f"🔍 DEBUG - Grupo: {grupo}, Sprint: {sprint}")
            print(f"  - Alunos avaliados: {sorted(df_sprint_last['nome_avaliado'].unique())}")
            print(f"  - Avaliadores (nomes): {sorted(df_sprint_last['nome_avaliador'].unique())}")
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
                denominador = 0.6 * (maior - menor) if maior != menor else 1
                df_result["Nota"] = ((df_result["Total"] - medias) / denominador).round(1)
            
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
            alunos = sorted(df_sprint_last["nome_avaliado"].unique())
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
