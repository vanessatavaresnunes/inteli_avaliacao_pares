# Configuração de Email com Variáveis de Ambiente

## Arquivo de Configuração

O sistema agora usa variáveis de ambiente para configuração de email. O arquivo principal é `config/email.env`.

## Como Configurar

1. **Copie o arquivo de exemplo:**
   ```bash
   cp config/env.example config/email.env
   ```

2. **Edite o arquivo `config/email.env` com suas credenciais:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=seu-email@gmail.com
   SENDER_PASSWORD=sua-senha-de-app
   USE_TLS=true
   APP_NAME=Sistema de Avaliação de Pares
   ```

## Variáveis Disponíveis

- `SMTP_SERVER`: Servidor SMTP (padrão: smtp.gmail.com)
- `SMTP_PORT`: Porta SMTP (padrão: 587)
- `SENDER_EMAIL`: Email remetente
- `SENDER_PASSWORD`: Senha do email (use senha de app para Gmail)
- `USE_TLS`: Usar TLS (true/false)
- `APP_NAME`: Nome da aplicação

## Segurança

- O arquivo `email.env` contém informações sensíveis
- Adicione `config/email.env` ao `.gitignore` se necessário
- Use senhas de aplicativo para Gmail

## Compatibilidade

O sistema mantém compatibilidade com o arquivo JSON antigo. Se o arquivo `email_config.json` existir, ele será usado. Caso contrário, as variáveis de ambiente serão carregadas.
