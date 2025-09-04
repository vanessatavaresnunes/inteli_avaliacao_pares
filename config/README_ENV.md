# Configuração de Variáveis de Ambiente

## Arquivos de Configuração

O sistema usa variáveis de ambiente para configuração do Supabase e email. Os arquivos principais são:
- `.env` (raiz do projeto) - Configurações do Supabase
- `config/email.env` - Configurações de email

## Como Configurar

1. **Configure o Supabase (arquivo `.env` na raiz):**
   ```bash
   cp config/env.example .env
   ```
   
   Edite o arquivo `.env` com suas credenciais do Supabase:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=sua-url-do-supabase
   NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=sua-chave-publishable
   BUCKET_NAME=inteli_avaliacao_pares_sprint
   ```

2. **Configure o Email (arquivo `config/email.env`):**
   ```bash
   cp config/env.example config/email.env
   ```
   
   Edite o arquivo `config/email.env` com suas credenciais de email:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=seu-email@gmail.com
   SENDER_PASSWORD=sua-senha-de-app
   USE_TLS=true
   APP_NAME=Sistema de Avaliação de Pares
   ```

## Variáveis Disponíveis

### Supabase (arquivo `.env`)
- `NEXT_PUBLIC_SUPABASE_URL`: URL do projeto Supabase
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY`: Chave publishable do Supabase
- `BUCKET_NAME`: Nome do bucket de armazenamento (padrão: inteli_avaliacao_pares_sprint)

### Email (arquivo `config/email.env`)
- `SMTP_SERVER`: Servidor SMTP (padrão: smtp.gmail.com)
- `SMTP_PORT`: Porta SMTP (padrão: 587)
- `SENDER_EMAIL`: Email remetente
- `SENDER_PASSWORD`: Senha do email (use senha de app para Gmail)
- `USE_TLS`: Usar TLS (true/false)
- `APP_NAME`: Nome da aplicação

## Segurança

- ⚠️ **IMPORTANTE**: Os arquivos `.env` e `config/email.env` contêm informações sensíveis e NÃO devem ser commitados no Git
- Os arquivos `.env` e `config/email.env` já estão no `.gitignore` para proteger suas credenciais
- Use senhas de aplicativo para Gmail (não use sua senha normal)
- Nunca compartilhe suas credenciais de Supabase ou email
- A chave `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` é segura para uso público (publishable)

### Como Configurar Gmail com Senha de App:

1. Ative a verificação em duas etapas na sua conta Google
2. Vá em "Gerenciar sua Conta do Google" > "Segurança"
3. Em "Como fazer login no Google", clique em "Senhas de app"
4. Selecione "Email" e "Outro (nome personalizado)"
5. Digite "Sistema de Avaliação de Pares"
6. Copie a senha gerada e use no arquivo `email.env`

## Compatibilidade

O sistema mantém compatibilidade com o arquivo JSON antigo. Se o arquivo `email_config.json` existir, ele será usado. Caso contrário, as variáveis de ambiente serão carregadas.
