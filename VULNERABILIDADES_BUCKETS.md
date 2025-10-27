# 🔒 Vulnerabilidades de Segurança - Buckets Supabase

## ⚠️ VULNERABILIDADES ENCONTRADAS

### **1. Exposição de URL do Supabase em Logs (MÉDIO)**

**Arquivo**: `src/utils/supabase_storage.py:50-51`

```python
except Exception as e:
    print(f"ERRO ao criar cliente Supabase: {e}")
    print(f"URL: {SUPABASE_URL}")  # ⚠️ VULNERABILIDADE
```

**Problema**: A URL do Supabase está sendo logada em produção.

**Impacto**: 
- Revela endpoint do banco de dados
- Facilitaria ataques direcionados
- Permite identificação do projeto Supabase

**Recomendação**: 
- ✅ Remover print da URL em produção
- ✅ Usar logging apropriado com nível ERROR
- ✅ Logar apenas se DEBUG estiver ativado

```python
# CORRETO:
import logging
logger = logging.getLogger(__name__)
logger.error(f"Erro ao criar cliente Supabase", exc_info=True)
```

---

### **2. Exposição de Key em Headers (BAIXO)**

**Arquivo**: `src/utils/supabase_storage.py:140-141`

```python
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    ...
}
```

**Problema**: Chave sendo enviada em headers de requisições HTTP.

**Análise**: 
- ✅ É chave **publishable** (anon key) - projetada para uso público
- ✅ Está no nome da variável: `NEXT_PUBLIC_`
- ⚠️ Mas ainda deve ser protegida da exposição desnecessária

**Recomendação**:
- ✅ Manter como está (é safe para publishable key)
- ✅ Confirmar que NUNCA usa service_role key

---

### **3. Falta de Validação de Autenticação (CRÍTICO)**

**Arquivo**: Múltiplos arquivos usando upload/download

```python
def upload_json_to_bucket(file_path: str, bucket_path: str, bucket_name: str = None):
    supabase = get_supabase_client()  # ⚠️ Sem validação de usuário
    bucket = bucket_name or BUCKET_NAME
    ...
    result = supabase.storage.from_(bucket).upload(...)
```

**Problema**: Não valida se o usuário está autenticado antes de fazer operações nos buckets.

**Impacto**: 
- Qualquer usuário autenticado pode acessar qualqual bucket
- Não há verificação de permissões específicas
- Falta controle de acesso baseado em turma/grupo

**Recomendação**:
```python
def upload_json_to_bucket(file_path: str, bucket_path: str, bucket_name: str = None, user_email: str = None):
    # Validar autenticação
    if not user_email:
        raise ValueError("Usuário não autenticado")
    
    # Validar permissão de acesso ao bucket
    if bucket_name and not user_has_bucket_permission(user_email, bucket_name):
        raise PermissionError("Usuário não tem permissão para este bucket")
    
    supabase = get_supabase_client()
    ...
```

---

### **4. Buckets Acessíveis por Qualquer Usuário (ALTO)**

**Problema**: Uma vez autenticado, qualquer usuário pode:
- Ler qualquer arquivo de qualquer bucket
- Fazer upload em qualquer bucket
- Listar conteúdo de buckets que não deveria acessar

**Exemplo**:
- Aluno T13 pode acessar bucket de T14
- Aluno 2025-2B pode acessar bucket de 2025-2A

**Mitigação Atual**: 
- ✅ RLS (Row-Level Security) configurada no Supabase
- ⚠️ Mas depende da configuração correta nas políticas SQL

**Recomendação**:
1. **Implementar validação no código**:
```python
def user_can_access_bucket(user_email: str, bucket_name: str) -> bool:
    """Verifica se usuário pode acessar o bucket"""
    user_data = get_user_data(user_email)
    user_period = get_period_for_user(user_email)
    bucket_period = get_period_for_bucket(bucket_name)
    
    return user_period == bucket_period
```

2. **Adicionar validação em TODAS as funções de bucket**:
```python
# Em upload_json_to_bucket
if not user_can_access_bucket(user_email, bucket_name):
    raise PermissionError("Acesso negado a este bucket")

# Em download_json_from_bucket
if not user_can_access_bucket(user_email, bucket_name):
    raise PermissionError("Acesso negado a este bucket")
```

---

### **5. Falta de Rate Limiting (BAIXO)**

**Problema**: Não há limite de requisições por usuário aos buckets.

**Impacto**:
- Possível abuso de API
- Custo elevado de requisições
- Possível DoS

**Recomendação**:
- ✅ Implementar cache de requisições
- ✅ Limitar número de uploads por período
- ✅ Adicionar debounce em operações frequentes

---

### **6. Logging Excessivo em Produção (BAIXO)**

**Arquivo**: Múltiplos arquivos

```python
print(f"🔄 Iniciando paginação para listar todos os arquivos...")
print(f"URL: {url}")
print(f"Bucket: {BUCKET_NAME}")
```

**Problema**: Muitos prints com informações do sistema.

**Impacto**:
- Logs podem expor estrutura do sistema
- Facilita reconnaissance por atacantes
- Aumenta risco de vazamento de informações

**Recomendação**:
- ✅ Usar sistema de logging apropriado
- ✅ Remover emojis de logs em produção
- ✅ Definir nível de log (DEBUG, INFO, ERROR)

```python
import logging
logger = logging.getLogger(__name__)

# Em desenvolvimento
logger.debug(f"URL: {url}")

# Em produção
# Não logar URLs ou informações sensíveis
```

---

## 🛡️ ANÁLISE DAS POLÍTICAS RLS

### **Status Atual das Políticas**

Verificar se as políticas SQL em `config_bucket_2025_2B.sql` foram aplicadas:

```sql
-- Políticas atuais (verificar se aplicadas):
CREATE POLICY "Allow public read access"
ON storage.objects FOR SELECT
USING (bucket_id = 'inteli_avalpares_2025_2B');

CREATE POLICY "Allow authenticated insert access"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'inteli_avalpares_2025_2B');
```

**Problema**: As políticas são muito permissivas:
- ✅ `SELECT` permite **qualquer pessoa** ler
- ✅ `INSERT` permite **qualquer usuário autenticado** escrever

**Recomendação**:
```sql
-- Políticas mais restritivas sugeridas:
CREATE POLICY "Restrict bucket access by period"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'inteli_avalpares_2025_2B' AND
    auth.uid() IN (
        SELECT id FROM usuarios WHERE periodo = '2025-2B'
    )
);
```

---

## 📋 CHECKLIST DE SEGURANÇA DOS BUCKETS

- [ ] **Remover prints de URL/KEY de logs**
- [ ] **Implementar validação de autenticação antes de upload/download**
- [ ] **Verificar permissões do usuário antes de acessar buckets**
- [ ] **Restringir políticas RLS no Supabase**
- [ ] **Adicionar rate limiting**
- [ ] **Usar logging apropriado ao invés de print()**
- [ ] **Validar que usuário só acessa bucket do seu período**
- [ ] **Implementar auditoria de acesso aos buckets**
- [ ] **Rotacionar credenciais regularmente**
- [ ] **Verificar que .env nunca é commitado**

---

## 🎯 PRIORIDADES

### **CRÍTICO - Fazer IMEDIATAMENTE**
1. ✅ Remover print da URL em erros
2. ✅ Implementar validação de permissões de bucket
3. ✅ Verificar e restringir políticas RLS

### **ALTO - Fazer em breve**
4. ⚠️ Adicionar validação de autenticação antes de operações
5. ⚠️ Implementar controle de acesso por período/turma

### **MÉDIO**
6. 📝 Substituir print() por logging apropriado
7. 📝 Adicionar rate limiting

---

## 📊 RESUMO DE RISCO

**Vulnerabilidades de Bucket**: 6 encontradas
- 🔴 Críticas: 1
- 🟠 Altas: 1
- 🟡 Médias: 2
- 🟢 Baixas: 2

**Status**: Requer atenção imediata antes de produção.

**Risco de Exposição de Dados**: **ALTO** se não implementar validações de acesso.

**Recomendação**: Implementar as correções críticas antes de permitir usuários reais no sistema.

