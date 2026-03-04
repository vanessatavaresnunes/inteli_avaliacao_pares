import os
import json
from src.utils.matricula_validator import MatriculaValidator
from src.controllers.avaliacao_controller import AvaliacaoController

with open("debug_results.txt", "w", encoding="utf-8") as f:
    f.write("--- TESTING MATRICULA VALIDATOR ---\n")
    validator = MatriculaValidator(periodo="2026-1A")
    
    grupos = validator.obter_grupos_por_turma('T17')
    f.write(f"Grupos T17: {grupos}\n")
    
    if grupos:
        grupo_teste = grupos[0]
        alunos = validator.obter_alunos_por_grupo('T17', grupo_teste)
        f.write(f"Alunos no {grupo_teste}: {json.dumps(alunos, indent=2)}\n")
    
    import streamlit as st
    st.session_state.user_authenticated = True
    st.session_state.logado = True
    st.session_state.turma_atual = "T17"
    
    if grupos:
        st.session_state.time_atual = grupos[0]
        alunos_grupo = validator.obter_alunos_por_grupo('T17', grupos[0])
        if alunos_grupo:
            st.session_state.aluno_atual = alunos_grupo[0]['nome']
            st.session_state.aluno_id_atual = alunos_grupo[0]['id']
            
            controller = AvaliacaoController(periodo="2026-1A")
            try:
                para_avaliar = controller.obter_alunos_para_avaliar()
                f.write(f"Alunos para avaliar ({st.session_state.aluno_atual}): {json.dumps(para_avaliar, indent=2)}\n")
            except Exception as e:
                f.write(f"Error: {e}\n")
