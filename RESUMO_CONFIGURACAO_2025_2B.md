# 📋 Resumo da Configuração 2025-2B

## ✅ Status
Sistema configurado e pronto para uso!

## 📦 Dados Configurados

### Turmas e Grupos - 2025-2B

#### T13 - 6 Grupos (43 alunos)
- **Grupo 1**: 7 alunos (IDs: 10, 13, 25, 27, 29, 36, 39)
- **Grupo 2**: 7 alunos (IDs: 1, 2, 3, 4, 5, 6, 7)
- **Grupo 3**: 8 alunos (IDs: 72, 19, 33, 34, 35, 37, 38, 43)
- **Grupo 4**: 7 alunos (IDs: 16, 24, 26, 28, 30, 31, 32)
- **Grupo 5**: 7 alunos (IDs: 15, 18, 17, 20, 21, 22, 41)
- **Grupo 6**: 7 alunos (IDs: 8, 9, 11, 12, 14, 23, 40)

#### T14 - 5 Grupos (25 alunos) - NOVA TURMA!
- **Grupo 1**: 5 alunos (IDs: 73-77)
  - Augustin, Bernardo, David, Enzo, Matheus
  
- **Grupo 2**: 5 alunos (IDs: 78-82)
  - Aymeric, Cibele, Fernanda, Gabriela, Mariana
  
- **Grupo 3**: 5 alunos (IDs: 83-87)
  - Igor, Isadora, Kaio, Leo, Marcelo
  
- **Grupo 4**: 5 alunos (IDs: 88-92)
  - Isabelly, Leonardo, Leonardo Martins, Mirella, Noémie
  
- **Grupo 5**: 5 alunos (IDs: 93-97)
  - Moyses, Pedro, Ricardo, Sacha, Thies

## 📅 Datas das Sprints 2025-2B

- **Sprint 1**: 15-24 out (avaliação: 24/10)
- **Sprint 2**: 27 out - 06 nov (avaliação: 06/11)
- **Sprint 3**: 10-19 nov (avaliação: 19/11)
- **Sprint 4**: 24 nov - 05 dez (avaliação: 05/12)
- **Sprint 5**: 08-18 dez (avaliação: 15/12)

## 🔧 Configurações

### Bucket Supabase
- **Bucket 2025-2A**: `inteli_avaliacao_pares_sprint` (antigo)
- **Bucket 2025-2B**: `inteli_avalpares_2025_2B` (novo) ✅ CRIADO

### Variáveis de Ambiente (.env)
```bash
NEXT_PUBLIC_SUPABASE_URL=https://mbdvsksqhoodhtsxawqn.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=[SUA_KEY]
PERIODO_ATUAL=2025-2B
```

### Email
- Configurado em: `config/email.env`
- Email: vanessa.nunes@prof.inteli.edu.br

## 🎯 Como Testar

1. Inicie o sistema:
   ```bash
   streamlit run app.py
   ```

2. Faça login com um email de teste (T13 ou T14)

3. Verifique:
   - ✅ Turma correto aparecendo
   - ✅ Grupos corretos (2025-2B)
   - ✅ Alunos corretos no grupo
   - ✅ Salvamento funcionando

## 📝 Arquivos Modificados

- `data/alunos.json` - Estrutura por período
- `data/usuarios/usuarios.json` - 25 novos alunos T14
- `data/sprint_dates_2025_2b.json` - Datas das sprints
- `.env` - Período e credenciais
- `src/models/usuario.py` - Suporte a período
- `src/utils/matricula_validator.py` - Suporte a período
- `src/utils/supabase_storage.py` - Função get_bucket_for_period()
- `src/models/avaliacao.py` - Salva no bucket correto
- Todos os scripts de análise atualizados

## 🚀 Pronto para Produção!

O sistema está totalmente configurado para 2025-2B. Você pode iniciar usando:
```bash
streamlit run app.py
```

