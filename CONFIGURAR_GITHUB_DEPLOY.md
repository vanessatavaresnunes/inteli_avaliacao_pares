# 🚀 Como Configurar Variáveis de Ambiente no GitHub/Servidor

## ⚠️ Por que ainda vejo 2025-2A no servidor?

O arquivo `.env` **NÃO** é commitado no GitHub por segurança (contém senhas). 

Você precisa configurar as variáveis de ambiente **diretamente no servidor/deploy**.

---

## 📋 Passo a Passo

### **1. No Servidor/Deploy (Streamlit Cloud, Heroku, etc.)**

Acesse as configurações do seu deploy e adicione estas variáveis:

```bash
# Configurações Supabase
NEXT_PUBLIC_SUPABASE_URL=https://mbdvsksqhoodhtsxawqn.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=sua-chave-aqui
BUCKET_NAME=inteli_avaliacao_pares_sprint

# ⚠️ PERÍODO ATUAL - ATUALIZE AQUI
PERIODO_ATUAL=2025-2B

# Ambiente
ENVIRONMENT=production

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=vanessa.nunes@prof.inteli.edu.br
SENDER_PASSWORD=nsty alxn hjds qgyx
USE_TLS=true
APP_NAME=Sistema de Avaliação de Pares
```

### **2. Como Adicionar em Streamlit Cloud**

1. Vá para: https://share.streamlit.io
2. Selecione seu app
3. Clique em "⚙️ Settings" (menu superior direito)
4. Role até "Secrets"
5. Cole as variáveis acima no formato:

```toml
[secrets]
NEXT_PUBLIC_SUPABASE_URL="https://mbdvsksqhoodhtsxawqn.supabase.co"
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY="sua-chave"
PERIODO_ATUAL="2025-2B"
ENVIRONMENT="production"
```

6. Salve e faça redeploy

---

### **3. Atualizar `config/env.example`**

Já atualizei o arquivo para você ter como referência.

---

## ✅ Arquivos que DEVEM estar no Git

- ✅ `config/env.example` (exemplo)
- ✅ `app.py`
- ✅ Código fonte
- ✅ `data/alunos.json`
- ✅ `data/usuarios/usuarios.json`

## ❌ Arquivos que NÃO DEVEM estar no Git

- ❌ `.env` (config local)
- ❌ `config/email.env` (senhas)
- ❌ Qualquer arquivo com credenciais

---

## 🎯 Verificação

Após configurar no servidor:

1. ✅ Verifica se `PERIODO_ATUAL=2025-2B` está configurado
2. ✅ Faz redeploy
3. ✅ Acessa o app e verifica que está em 2025-2B

---

## 📝 Comandos Úteis

### **Verificar variáveis no servidor:**
```bash
# No terminal do servidor
env | grep PERIODO_ATUAL
```

### **Commitar mudanças (código):**
```bash
git add .
git commit -m "Update para 2025-2B"
git push
```

### **Forçar redeploy:**
```bash
# No Streamlit Cloud, apenas clique em "Always rerun"
# Ou faça um push vazio:
git commit --allow-empty -m "Trigger redeploy"
git push
```

