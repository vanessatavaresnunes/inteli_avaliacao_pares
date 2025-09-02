# 🔒 Guia de Segurança - Sistema de Avaliação de Pares

## ⚠️ CREDENCIAIS SENSÍVEIS

**NUNCA** commite credenciais reais no repositório Git!

### Arquivos que NÃO devem ser commitados:
- `config/email.env` (contém senha de email)
- `config/email_config.json` (contém credenciais)
- Qualquer arquivo `.env` com credenciais reais

### Arquivos seguros para commit:
- `config/env.example` (template sem credenciais reais)
- `config/README_ENV.md` (documentação)
- `SECURITY.md` (este arquivo)

## 🛡️ Como Configurar Credenciais de Forma Segura

### 1. Para Gmail (Recomendado):

1. **Ative a verificação em duas etapas** na sua conta Google
2. **Gere uma senha de app**:
   - Vá em "Gerenciar sua Conta do Google" > "Segurança"
   - Em "Como fazer login no Google", clique em "Senhas de app"
   - Selecione "Email" e "Outro (nome personalizado)"
   - Digite "Sistema de Avaliação de Pares"
   - **Copie a senha gerada** (16 caracteres sem espaços)

3. **Configure o arquivo `config/email.env`**:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=seu-email@gmail.com
   SENDER_PASSWORD=abcd-efgh-ijkl-mnop
   USE_TLS=true
   APP_NAME=Sistema de Avaliação de Pares
   ```

### 2. Para Outros Provedores:

- **Outlook/Hotmail**: Use autenticação OAuth2
- **Yahoo**: Configure senha de app
- **Provedores corporativos**: Consulte o administrador

## 🔍 Verificação de Segurança

### Antes de fazer commit, verifique:

```bash
# Verificar se há credenciais no código
git status
git diff --cached

# Procurar por padrões suspeitos
grep -r "password\|senha\|@.*\.com" --exclude-dir=.git .
```

### Se encontrar credenciais:

1. **NÃO faça commit**
2. **Remova as credenciais** do arquivo
3. **Use o arquivo de exemplo** como base
4. **Configure localmente** com suas credenciais

## 🚨 Se Credenciais Foram Expostas

1. **Altere imediatamente** a senha do email
2. **Revogue** senhas de app antigas
3. **Gere novas** senhas de app
4. **Atualize** o arquivo local `config/email.env`

## 📋 Checklist de Segurança

- [ ] Arquivo `config/email.env` está no `.gitignore`
- [ ] Usando senha de app (não senha normal)
- [ ] Credenciais não estão no código
- [ ] Arquivo de exemplo não tem credenciais reais
- [ ] Documentação explica configuração segura

## 🆘 Suporte

Se tiver dúvidas sobre segurança:
1. Consulte este arquivo
2. Verifique a documentação em `config/README_ENV.md`
3. Entre em contato com o administrador do sistema
