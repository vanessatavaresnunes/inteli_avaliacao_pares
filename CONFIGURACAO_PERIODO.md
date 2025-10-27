# Configuração de Período e Bucket

Este documento explica como configurar o período acadêmico e o bucket de armazenamento.

## Período Atual

O sistema usa uma variável de ambiente global `PERIODO_ATUAL` para determinar qual período acadêmico está ativo.

### Configuração

1. **Criar ou editar arquivo `.env` ou `config/email.env`**:
   ```bash
   # Período acadêmico atual
   PERIODO_ATUAL=2025-2B
   ```

2. **Estrutura de buckets por período**:
   - **2025-2A**: `inteli_avaliacao_pares_sprint`
   - **2025-2B**: `inteli_avalpares_2025_2B`

## Como Funciona

O sistema determina automaticamente qual bucket usar baseado no período configurado:

```python
from src.utils.supabase_storage import get_bucket_for_period

# Bucket padrão (2025-2A)
bucket = get_bucket_for_period("2025-2A")  
# Retorna: "inteli_avaliacao_pares_sprint"

# Bucket para 2025-2B
bucket = get_bucket_for_period("2025-2B")
# Retorna: "inteli_avalpares_2025_2B"
```

## Migração para 2025-2B

Quando mudar de período, você precisa:

1. **Atualizar a variável de ambiente**:
   ```bash
   PERIODO_ATUAL=2025-2B
   ```

2. **Configurar o novo bucket no Supabase**:
   - Acesse o Supabase Dashboard
   - Vá em Storage
   - Crie um novo bucket chamado: `inteli_avalpares_2025_2B` (já criado!)
   - Configure as políticas de acesso (se necessário)

3. **Atualizar dados de alunos**:
   - Preencher `data/alunos.json` com dados do período 2025-2B
   - Os dados de 2025-2A continuarão no bucket antigo

## Estrutura de Dados

### alunos.json
```json
{
  "2025-2A": {
    "T09": { "Grupo 1": [...] },
    "T13": { "Grupo 1": [...] }
  },
  "2025-2B": {
    "T09": { "Grupo 1": [...] },
    "T13": { "Grupo 1": [...] }
  }
}
```

## Compatibilidade

- O sistema mantém compatibilidade retroativa com 2025-2A
- Dados antigos continuam acessíveis no bucket original
- Análises podem ser feitas especificando o período

## Exemplos de Uso

### Em scripts de análise
```python
# Buscar avaliações do período atual
df = buscar_avaliacoes_por_turma_sprint("T13", "Sprint 1", periodo="2025-2B")
```

### Em uploads
```python
from src.utils.supabase_storage import upload_json_to_bucket, get_bucket_for_period

periodo = "2025-2B"
bucket = get_bucket_for_period(periodo)
upload_json_to_bucket(arquivo, caminho, bucket_name=bucket)
```
