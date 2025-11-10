# 🚀 Como Configurar PERIODO_ATUAL no Streamlit Cloud

## ❌ Problema Atual

Você consegue ver os alunos localmente, mas **não vê na produção (Streamlit Cloud)**.

Isso acontece porque a variável de ambiente `PERIODO_ATUAL` **NÃO está configurada** no Streamlit Cloud.

---

## ✅ Solução: 3 Passos Simples

### Passo 1: Acessar Streamlit Cloud
1. Acesse: https://share.streamlit.io
2. Faça login com sua conta GitHub
3. Clique no seu app (ex: "inteli_avaliacao_pares")

### Passo 2: Configurar Variável de Ambiente
1. Clique no menu **"⚙️ Settings"** (canto superior direito)
2. Na página de configurações, role até a seção **"Secrets"**
3. Clique no botão **"Open secrets editor"** ou edite diretamente

### Passo 3: Adicionar PERIODO_ATUAL
Cole este conteúdo no editor de secrets:

```toml
# Período Acadêmico Atual
PERIODO_ATUAL = "2025-2B"

# Supabase (ajuste com suas credenciais)
NEXT_PUBLIC_SUPABASE_URL = "https://mbdvsksqhoodhtsxawqn.supabase.co"
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY = "sua-chave-publica-aqui"
BUCKET_NAME = "inteli_avaliacao_pares_sprint"

# Ambiente
ENVIRONMENT = "production"

# Email (se necessário)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "seu-email@exemplo.com"
SENDER_PASSWORD = "sua-senha-app"
USE_TLS = "true"
APP_NAME = "Sistema de Avaliação de Pares"
```

4. Clique em **"Save"**

### Passo 4: Fazer Redeploy
1. Volte para a página principal do app
2. Clique em **"Manage app"** (três pontos no canto direito)
3. Selecione **"Always rerun"** ou **"Redeploy"**

OU

1. No menu superior, clique em **"⋮" (três pontos)**
2. Selecione **"Restart app"**

---

## 🔍 Como Verificar se Funcionou

Após o redeploy:
1. Acesse seu app no Streamlit Cloud
2. Faça login com `pedro.faria@sou.inteli.edu.br` (senha: `123456`)
3. Na tela de avaliação, **devem aparecer os alunos do Grupo 5 da T14**:
   - Moyses Birman Anijar (ID 93)
   - Pedro El Haouli Faria (ID 94) - você mesmo
   - Ricardo de Toledo Planas (ID 95)
   - Sacha Kefif (ID 96)
   - Thies David Hillen (ID 97)

**OBS:** Você não vê a si mesmo na lista (está excluído automaticamente).

---

## ⚠️ Troubleshooting

### Problema: "Ainda não vejo os alunos"
**Solução:** 
1. Verifique se `PERIODO_ATUAL = "2025-2B"` está correto (com aspas duplas)
2. Faça um novo redeploy
3. Limpe o cache do navegador (Ctrl+Shift+Delete)

### Problema: "Erro ao conectar com Supabase"
**Solução:**
1. Verifique se as credenciais do Supabase estão corretas
2. Verifique se o bucket `inteli_avalpares_2025_2B` existe no Supabase
3. Verifique as políticas RLS do bucket

### Problema: "Não consigo fazer login"
**Solução:**
1. Verifique se o usuário existe em `data/usuarios/usuarios.json`
2. Use a senha de teste: `123456`
3. Verifique se o email está em minúsculas

---

## 📝 Notas Importantes

- ✅ O arquivo `.env` **NÃO é commitado** no GitHub por segurança
- ✅ As configurações no Streamlit Cloud são **independentes** do código local
- ✅ **SEMPRE** configure no Streamlit Cloud após mudanças de período
- ✅ O período local não afeta o período de produção

---

## 📞 Dúvidas?

Se ainda não funcionar:
1. Veja os logs do Streamlit Cloud (menu "Manage app" → "Logs")
2. Procure por mensagens de erro relacionadas a `PERIODO_ATUAL`
3. Verifique se o arquivo `alunos.json` está atualizado no GitHub





