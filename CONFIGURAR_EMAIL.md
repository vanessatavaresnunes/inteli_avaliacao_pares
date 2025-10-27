# 📧 Configuração de Email

## ⚠️ Problema Atual

As credenciais de email no arquivo `config/email.env` não estão funcionando. O erro indica que o Gmail não aceita o usuário e senha.

## 🔧 Como Corrigir

### **Opção 1: Gerar Nova "App Password" do Google**

1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione a conta: `vanessa.nunes@prof.inteli.edu.br`
3. Escolha "Mail" e "Other (Custom name)"
4. Digite: "Sistema de Avaliação de Pares"
5. Clique em "Generate"
6. **Copie a senha gerada** (16 caracteres, exemplo: `abcd efgh ijkl mnop`)

### **Opção 2: Usar Senha de App Existente**

Se você já tem uma "App Password":
1. Abra o arquivo `config/email.env`
2. Substitua a linha:
   ```
   SENDER_PASSWORD=nsty alxn hjds qgyx
   ```
   Pela nova senha:
   ```
   SENDER_PASSWORD=SUA_NOVA_SENHA_AQUI
   ```

### **Opção 3: Usar Outro Email**

Se preferir usar outro email (não Gmail):

1. Abra `config/email.env`
2. Alterar as configurações:

```env
# Para Gmail/Google Workspace
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=seu-email@gmail.com
SENDER_PASSWORD=sua-app-password
USE_TLS=true

# Para Outlook/Microsoft 365
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SENDER_EMAIL=seu-email@outlook.com
SENDER_PASSWORD=sua-senha-normal
USE_TLS=true

# Para Outlook (IMAP)
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=seu-email@outlook.com
SENDER_PASSWORD=sua-senha-normal
USE_TLS=true
```

## 📝 Arquivo Atual

O arquivo `config/email.env` está configurado assim:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=vanessa.nunes@prof.inteli.edu.br
SENDER_PASSWORD=nsty alxn hjds qgyx
USE_TLS=true
APP_NAME=Sistema de Avaliação de Pares
```

## ✅ Como Validar

Após atualizar as credenciais:

1. Salve o arquivo `config/email.env`
2. Tente enviar uma avaliação novamente
3. O email deve ser enviado com sucesso

## 🚫 Alternativa: Desabilitar Email

Se não quiser configurar email agora:

1. O sistema continuará funcionando normalmente
2. As avaliações serão salvas no Supabase
3. Apenas o envio de email ficará desabilitado (não é obrigatório)

---

**Nota**: O sistema **não depende** de email para funcionar. As avaliações são sempre salvas no Supabase independentemente do email.

