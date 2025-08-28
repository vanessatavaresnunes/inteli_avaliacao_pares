#!/usr/bin/env python3
"""
Script para alterar o campo 'username' para 'name' no usuarios.json
"""

import json
from pathlib import Path

def main():
    print("🔄 Alterando campo 'username' para 'name'...")
    
    # Caminho do arquivo
    usuarios_file = Path("data/usuarios/usuarios.json")
    
    # Carregar dados
    try:
        with open(usuarios_file, 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        print(f"✅ Arquivo carregado com {len(usuarios)} usuários")
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return
    
    # Alterar campo username para name
    usuarios_alterados = {}
    for email, usuario in usuarios.items():
        # Criar novo usuário com campo 'name' em vez de 'username'
        novo_usuario = {}
        for campo, valor in usuario.items():
            if campo == "username":
                novo_usuario["name"] = valor
                print(f"🔄 {campo} → name: {valor}")
            else:
                novo_usuario[campo] = valor
        
        usuarios_alterados[email] = novo_usuario
    
    # Salvar arquivo alterado
    try:
        with open(usuarios_file, 'w', encoding='utf-8') as f:
            json.dump(usuarios_alterados, f, indent=2, ensure_ascii=False)
        print(f"✅ Arquivo salvo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return
    
    # Mostrar estrutura final
    print("\n📋 ESTRUTURA FINAL DO usuarios.json:")
    print("  - name: Nome do usuário (antes username)")
    print("  - password_hash: Hash da senha (vazio se pré-cadastrado)")
    print("  - turma: Turma do aluno")
    print("  - aluno_id: ID único do aluno (apenas para alunos)")
    
    print(f"\n🎉 Campo 'username' alterado para 'name' em {len(usuarios)} usuários!")

if __name__ == "__main__":
    main()

