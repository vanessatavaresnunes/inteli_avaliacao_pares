import streamlit as st
import pandas as pd
from src.utils.supabase_storage import list_json_files_in_bucket, download_json_from_bucket
import json
from collections import defaultdict

st.set_page_config(page_title="Análise das Avaliações", layout="wide")

st.title("🔎 Análise das Avaliações de Pares")

# Carregar todos os arquivos de avaliações


# Listar arquivos do bucket Supabase
arquivos = list_json_files_in_bucket(prefix="aval_")
if not arquivos:
    st.warning("Nenhum dado de avaliação encontrado no Supabase.")
    st.stop()

# Identificar turmas a partir dos nomes dos arquivos
turmas = set()
for arq in arquivos:
    partes = arq.split('_')
    if len(partes) > 2:
        turmas.add(partes[1])
turmas = sorted(list(turmas))
if not turmas:
    st.warning("Nenhuma turma encontrada nos arquivos de avaliação.")
    st.stop()

turma_selecionada = st.selectbox("Selecione a turma para análise:", turmas, key="analise_turma")

# Filtrar arquivos da turma selecionada
arquivos_turma = [arq for arq in arquivos if f"_{turma_selecionada}_" in arq]
if not arquivos_turma:
    st.warning(f"Nenhum dado de avaliação encontrado para a turma {turma_selecionada}.")
    st.stop()

# Carregar dados em DataFrame
linhas = []
import tempfile
for arq in arquivos_turma:
    if arq.startswith("avaliacoescompletas"):
        continue
    with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as tmp:
        download_json_from_bucket(arq, tmp.name)
        tmp.seek(0)
        conteudo = tmp.read().decode("utf-8").strip()
        if conteudo:
            for linha in conteudo.splitlines():
                linha = linha.strip()
                if linha:
                    try:
                        dado = json.loads(linha)
                        linhas.append(dado)
                    except Exception as e:
                        pass
if not linhas:
    st.warning("Nenhum dado de avaliação encontrado.")
    st.stop()
df = pd.DataFrame(linhas)

# Garantir colunas essenciais
for col in ["time", "sprint", "nome_avaliado", "eixo", "nota"]:
    if col not in df.columns:
        st.error(f"Coluna obrigatória ausente: {col}")
        st.stop()

grupos = sorted(df["time"].unique())
sprints = sorted(df["sprint"].unique())

for grupo in grupos:
    with st.expander(f"Grupo: {grupo}", expanded=False):
        df_grupo = df[df["time"] == grupo]
        for sprint in sprints:
            df_sprint = df_grupo[df_grupo["sprint"] == sprint]
            if df_sprint.empty:
                continue
            # Manter apenas a última avaliação de cada avaliador para cada avaliado/eixo
            df_sprint_sorted = df_sprint.sort_values("timestamp")
            df_sprint_last = df_sprint_sorted.groupby([
                "id_avaliador", "id_avaliado", "eixo"
            ], as_index=False).last()
            st.subheader(f"Sprint: {sprint}")
            alunos = sorted(df_sprint_last["nome_avaliado"].unique())
            eixos = sorted(df_sprint_last["eixo"].unique())
            # Montar tabela de somatórios e checar status de avaliações
            dados = []
            n_avaliadores = len(df_sprint_last["id_avaliador"].unique())
            for aluno in alunos:
                linha = {}
                # Checar se o aluno recebeu todas as avaliações esperadas (por eixo)
                completo = True
                faltou = False
                for eixo in eixos:
                    avals = df_sprint_last[(df_sprint_last["nome_avaliado"] == aluno) & (df_sprint_last["eixo"] == eixo)]
                    soma = avals["nota"].sum()
                    linha[eixo] = soma
                    # Esperado: 1 avaliação de cada avaliador (exceto autoavaliação)
                    n_recebidas = len(avals)
                    if n_recebidas < n_avaliadores - 1:
                        completo = False
                # Checar se o aluno fez avaliações (como avaliador)
                fez_avaliacao = aluno in df_sprint_last["nome_avaliador"].unique() or aluno in df_sprint_last["id_avaliador"].unique()
                if not fez_avaliacao:
                    completo = False
                linha["Total"] = sum(linha[eixo] for eixo in eixos)
                # Nome colorido conforme status
                if completo:
                    linha["Aluno"] = f'<span style="color:green;font-weight:bold">{aluno}</span>'
                else:
                    linha["Aluno"] = f'<span style="color:red;font-weight:bold">{aluno}</span>'
                dados.append(linha)
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

# Exibir feedbacks recebidos por cada aluno em tabela colapsável (fora dos expanders de grupo)
with st.expander("Feedbacks recebidos por aluno (tabela)", expanded=False):
    feedback_data = []
    # Para todos os grupos e sprints
    for grupo in grupos:
        df_grupo = df[df["time"] == grupo]
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
    df_feedback = pd.DataFrame(feedback_data)
    # Garante ordem das colunas: Grupo, Sprint, Aluno, Entregas reais, Valor Percebido, Caixa de Ferramentas
    colunas = ["Grupo", "Sprint", "Aluno", "Entregas reais", "Valor Percebido", "Caixa de Ferramentas"]
    df_feedback = df_feedback[colunas]

    # Filtros de grupo e sprint
    grupos_unicos = sorted(df_feedback["Grupo"].unique())
    grupo_sel = st.selectbox("Filtrar por grupo:", options=["Todos"] + grupos_unicos, index=0)
    sprints_unicos = sorted(df_feedback["Sprint"].unique())
    sprint_sel = st.selectbox("Filtrar por sprint:", options=["Todos"] + sprints_unicos, index=0)

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
