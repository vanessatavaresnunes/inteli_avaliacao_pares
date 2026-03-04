import json
import re

usuarios_path = r'c:\Users\Inteli\OneDrive\Documentos\MeusProjetos\inteli_ aval_pares_sprint\data\usuarios\usuarios.json'
alunos_path = r'c:\Users\Inteli\OneDrive\Documentos\MeusProjetos\inteli_ aval_pares_sprint\data\alunos.json'

with open(usuarios_path, 'r', encoding='utf-8') as f:
    usuarios = json.load(f)

# Create email -> id mapping
email_to_id = {email.lower(): data['id'] for email, data in usuarios.items()}

raw_data = """Alexsander da Silva Barbosa	alexsander.barbosa@sou.inteli.edu.br	2
Ana Cristina Alves Jardim	ana.jardim@sou.inteli.edu.br	5
Anny Jhulia Cerazi	anny.cerazi@sou.inteli.edu.br	2
Carlos Eduardo Serrano Quaglia	carlos.quaglia@sou.inteli.edu.br	1
Catarina Sayuri Arashiro Braga Felipe	catarina.felipe@sou.inteli.edu.br	3
Celso Rodrigues Rocha Júnior	celso.junior@sou.inteli.edu.br	3
Débora Pereira Nogueira	debora.nogueira@sou.inteli.edu.br	5
Eduardo Alonso Casarini	eduardo.casarini@sou.inteli.edu.br	2
Emanuelly Cantarelli Dias	emanuelly.dias@sou.inteli.edu.br	4
Felipe Freire Machado Simão	felipe.simao@sou.inteli.edu.br	4
Felipe Neves Teixeira da Silva	felipe.teixeira@sou.inteli.edu.br	2
Gabriel Andrei dos Reis	gabriel.reis@sou.inteli.edu.br	3
Giacomo Zema Matizonkas	giacomo.matizonkas@sou.inteli.edu.br	1
Henrique Milliorini Botti	henrique.botti@sou.inteli.edu.br	1
Henrique Rodrigues Diniz	henrique.diniz@sou.inteli.edu.br	3
Isaac Souza Santos	isaac.santos@sou.inteli.edu.br	4
Jaime Andrade de Almeida	jaime.almeida@sou.inteli.edu.br	5
Karol Rocha Barbosa	karol.barbosa@sou.inteli.edu.br	2
Leonardo Ramos Vieira	leonardo.vieira@sou.inteli.edu.br	3
Lucas Picinato Rogero	lucas.rogero@sou.inteli.edu.br	1
Mariana Lacerda Reis	mariana.reis@sou.inteli.edu.br	4
Mariana Pereira de Souza	mariana.pereira@sou.inteli.edu.br	1
Matheus Ferreira da Silva	matheus.silva@sou.inteli.edu.br	5
Mirela Schneider Bianchi	mirela.bianchi@sou.inteli.edu.br	1
Nicholas Anantha Krishnan Milla	nicholas.millani@sou.inteli.edu.br	1
Nicole Zanin Silva	nicole.silva@sou.inteli.edu.br	3
Owen Ahmed Robert Paimba-sai	owen.paimba-sail@sou.inteli.edu.br	5
Paulo Henrique Bueno Fernandes	paulo.fernandes@sou.inteli.edu.br	2
Rafael Figueiredo Campos	rafael.campos@sou.inteli.edu.br	3
Rui Miranda Ribeiro Facó	rui.faco@sou.inteli.edu.br	2
Tobias Viana Araújo	tobias.araujo@sou.inteli.edu.br	4
Vinicius Alves Maciel	vinicius.maciel@sou.inteli.edu.br	4
Vitor Ribeiro de Mattos Silva	vitor.silva@sou.inteli.edu.br	5
Wendel Hebert Feitosa	wendel.feitosa@sou.inteli.edu.br	4
Yudi Nakamura Trevisani Omaki	yudi.omaki@sou.inteli.edu.br	5"""

grupos = {}

for line in raw_data.strip().split('\n'):
    parts = line.split('\t')
    if len(parts) >= 3:
        email = parts[1].strip().lower()
        grupo_num = parts[2].strip()
        grupo_name = f"Grupo {grupo_num}"
        
        if email not in email_to_id:
            print(f"Warning: email {email} not found in usuarios.json!")
            continue
            
        student_id = email_to_id[email]
        
        if grupo_name not in grupos:
            grupos[grupo_name] = []
        grupos[grupo_name].append(student_id)

# Sort the items
sorted_grupos = {k: sorted(v) for k, v in sorted(grupos.items())}

# Update alunos.json
with open(alunos_path, 'r', encoding='utf-8') as f:
    alunos = json.load(f)

if "2026-1A" not in alunos:
    alunos["2026-1A"] = {}

alunos["2026-1A"]["T17"] = sorted_grupos

with open(alunos_path, 'w', encoding='utf-8') as f:
    json.dump(alunos, f, indent=2, ensure_ascii=False)

print("Grupos updated successfully in alunos.json!")
