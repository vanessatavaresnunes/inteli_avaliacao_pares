# 🔒 Relatório de Segurança

## ⚠️ VULNERABILIDADES CRÍTICAS

### **1. Senha de Teste Hardcoded (CRÍTICO)**
**Arquivo**: `src/utils/user_storage.py:154-159`

```python
# SENHA DE TESTE: Permitir "123456" para qualquer usuário
if password == "123456":
    print(f"[TESTE] Login aceito com senha de teste para {email_normalizado}")
    self.audit_logger.log_login(email_normalizado)
    return True, user
```

**Problema**: Qualquer pessoa pode fazer login com senha "123456" em QUALQUER conta do sistema.

**Impacto**: Acesso completo ao sistema para qualquer usuário.

**Recomendação**: 
- ✅ Remover em produção
- ✅ Habilitar apenas para ambiente de desenvolvimento
- ✅ Usar variável de ambiente `ALLOW_TEST_PASSWORD=false` em produção

---

### **2. Uso de eval() (ALTO)**
**Arquivo**: `src/models/usuario.py:189`

```python
if re.match(r'^[\d\+\-\*\/\(\)\s]+$', expressao):
    return max(1, int(eval(expressao)))
```

**Problema**: `eval()` pode executar código arbitrário se a expressão for malformada.

**Mitigação**: Já existe validação com regex, mas `eval()` ainda é perigoso.

**Recomendação**:
- ✅ Substituir `eval()` por parsing manual
- ✅ Ou usar biblioteca como `simpleeval` (mais segura)

---

### **3. Logging de Dados Sensíveis (MÉDIO)**
**Arquivo**: `src/utils/email_service.py:32-33`

```python
print(f"DEBUG - Email carregado: {email}")
print(f"DEBUG - Password carregado: {'*' * len(password) if password else 'VAZIO'}")
```

**Problema**: Email sendo logado em produção.

**Impacto**: Email de usuários pode ser exposto em logs.

**Recomendação**:
- ✅ Remover logs de debug em produção
- ✅ Usar nível de log apropriado (DEBUG vs INFO vs ERROR)

---

### **4. Credenciais em Arquivos de Configuração (MÉDIO)**
**Arquivos**: 
- `config/email.env` - Contém senha de app do Gmail
- `.env` - Contém chaves Supabase

**Problema**: Se commitados por acidente, credenciais ficam no Git.

**Mitigação**: Já está em `.gitignore`, mas precisa verificar.

**Recomendação**:
- ✅ Confirmar que `config/email.env` e `.env` estão em `.gitignore`
- ✅ Usar secrets manager em produção
- ✅ Rotacionar credenciais regularmente

---

### **5. Sem Proteção CSRF (BAIXO)**
**Framework**: Streamlit

**Problema**: Streamlit não tem proteção CSRF nativa.

**Impacto**: Possível ataque cross-site request forgery.

**Recomendação**:
- ✅ Adicionar tokens CSRF para operações sensíveis
- ✅ Validar origem de requisições

---

### **6. Falta de Rate Limiting (BAIXO)**
**Problema**: Não há limite de tentativas de login.

**Impacto**: Possível brute force attack.

**Recomendação**:
- ✅ Implementar limite de tentativas (ex: 5 tentativas por 15 minutos)
- ✅ Bloquear IP após muitas tentativas

---

## ✅ PONTOS POSITIVOS DE SEGURANÇA

### **1. Senhas Criptografadas**
✅ Usa bcrypt para hash de senhas
✅ Não armazena senhas em texto plano

### **2. Validação de Email Institucional**
✅ Apenas emails @sou.inteli.edu.br e @prof.inteli.edu.br são aceitos

### **3. Auditoria de Acessos**
✅ Log de login bem-sucedidos e falhas
✅ Log de alterações de senha
✅ Log de avaliações enviadas

### **4. Row-Level Security no Supabase**
✅ Políticas RLS configuradas para buckets

### **5. Validação de Dados de Entrada**
✅ Validação de notas
✅ Validação de feedbacks
✅ Validação de formato de email

---

## 🛠️ AÇÕES RECOMENDADAS

### **PRIORIDADE ALTA** (Fazer IMEDIATAMENTE)

1. **Remover senha de teste "123456"**
   ```python
   # REMOVER estas linhas em produção:
   if password == "123456":
       return True, user
   ```

2. **Adicionar variável de ambiente para testar**
   ```python
   # Permitir senha de teste APENAS em desenvolvimento
   TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
   if TEST_MODE and password == "123456":
       # permitir apenas em TEST_MODE
   ```

3. **Remover logs de debug em produção**
   ```python
   # Usar logging apropriado
   import logging
   logger = logging.getLogger(__name__)
   logger.debug(f"Email: {email}")  # Não em produção
   ```

### **PRIORIDADE MÉDIA**

4. **Substituir eval() por parsing seguro**
5. **Implementar rate limiting em login**
6. **Adicionar proteção CSRF**
7. **Rotacionar credenciais regularmente**

---

## 📋 CHECKLIST DE SEGURANÇA ANTES DE DEPLOY EM PRODUÇÃO

- [ ] Remover senha de teste "123456"
- [ ] Remover todos os print() de debug
- [ ] Substituir eval() por parsing seguro
- [ ] Verificar que .env e email.env estão em .gitignore
- [ ] Configurar ALLOW_TEST_PASSWORD=false
- [ ] Ativar rate limiting
- [ ] Implementar proteção CSRF
- [ ] Backup de dados sensíveis
- [ ] Revisar permissões de arquivos (chmod 600 para .env)
- [ ] Ativar logs de segurança

---

## 📊 RESUMO

**Vulnerabilidades Encontradas**: 6
- 🔴 Críticas: 1
- 🟠 Altas: 1
- 🟡 Médias: 2
- 🟢 Baixas: 2

**Status Geral**: Requer atenção antes de deploy em produção.

**Risco**: ALTO se senha de teste "123456" ainda ativa.

