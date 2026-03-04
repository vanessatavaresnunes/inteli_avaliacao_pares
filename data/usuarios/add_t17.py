import json
import os

data_path = r'c:\Users\Inteli\OneDrive\Documentos\MeusProjetos\inteli_ aval_pares_sprint\data\usuarios\usuarios.json'

new_users_raw = """Alexsander da Silva Barbosa		Alexsander.Barbosa@sou.inteli.edu.br
Ana Cristina Alves Jardim		Ana.Jardim@sou.inteli.edu.br
Anny Jhulia Cerazi		Anny.Cerazi@sou.inteli.edu.br
Carlos Eduardo Serrano Quaglia		Carlos.Quaglia@sou.inteli.edu.br
Catarina Sayuri Arashiro Braga Felipe		Catarina.Felipe@sou.inteli.edu.br
Celso Rodrigues Rocha Júnior		Celso.Junior@sou.inteli.edu.br
Débora Pereira Nogueira		Debora.Nogueira@sou.inteli.edu.br
Eduardo Alonso Casarini		Eduardo.Casarini@sou.inteli.edu.br
Emanuelly Cantarelli Dias		Emanuelly.Dias@sou.inteli.edu.br
Felipe Freire Machado Simão		Felipe.Simao@sou.inteli.edu.br
Felipe Neves Teixeira da Silva		Felipe.Teixeira@sou.inteli.edu.br
Gabriel Andrei dos Reis		Gabriel.Reis@sou.inteli.edu.br
Giacomo Zema Matizonkas		Giacomo.Matizonkas@sou.inteli.edu.br
Henrique Milliorini Botti		Henrique.Botti@sou.inteli.edu.br
Henrique Rodrigues Diniz		Henrique.Diniz@sou.inteli.edu.br
Isaac Souza Santos		Isaac.Santos@sou.inteli.edu.br
Jaime Andrade de Almeida		Jaime.Almeida@sou.inteli.edu.br
Karol Rocha Barbosa		Karol.Barbosa@sou.inteli.edu.br
Leonardo Ramos Vieira		Leonardo.Vieira@sou.inteli.edu.br
Lucas Picinato Rogero		Lucas.Rogero@sou.inteli.edu.br
Mariana Lacerda Reis		Mariana.Reis@sou.inteli.edu.br
Mariana Pereira de Souza		Mariana.Pereira@sou.inteli.edu.br
Matheus Ferreira da Silva		Matheus.Silva@sou.inteli.edu.br
Mirela Schneider Bianchi		Mirela.Bianchi@sou.inteli.edu.br
Nicholas Anantha Krishnan Millani		Nicholas.Millani@sou.inteli.edu.br
Nicole Zanin Silva		Nicole.Silva@sou.inteli.edu.br
Owen Ahmed Robert Paimba-Sail		Owen.Paimba-Sail@sou.inteli.edu.br
Paulo Henrique Bueno Fernandes		Paulo.Fernandes@sou.inteli.edu.br
Rafael Figueiredo Campos		Rafael.Campos@sou.inteli.edu.br
Rui Miranda Ribeiro Facó		Rui.Faco@sou.inteli.edu.br
Tobias Viana Araújo		Tobias.Araujo@sou.inteli.edu.br
Vinicius Alves Maciel		Vinicius.Maciel@sou.inteli.edu.br
Vitor Ribeiro de Mattos Silva		Vitor.Silva@sou.inteli.edu.br
Wendel Hebert Feitosa		Wendel.Feitosa@sou.inteli.edu.br
Yudi Nakamura Trevisani Omaki		Yudi.Omaki@sou.inteli.edu.br"""

with open(data_path, 'r', encoding='utf-8') as f:
    usuarios = json.load(f)

max_id = max([u['id'] for u in usuarios.values()])

for line in new_users_raw.strip().split('\n'):
    if not line.strip(): continue
    parts = line.split('\t')
    if len(parts) >= 2:
        name = parts[0].strip()
        email = parts[-1].strip().lower()
        if email in usuarios:
            usuarios[email]['turma'] = 'T17'
            usuarios[email]['name'] = name # Update name just in case
        else:
            max_id += 1
            usuarios[email] = {
                "name": name,
                "passwd": "",
                "turma": "T17",
                "id": max_id
            }

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(usuarios, f, indent=2, ensure_ascii=False)

print(f"Added/updated users. Total users now: {len(usuarios)}")
