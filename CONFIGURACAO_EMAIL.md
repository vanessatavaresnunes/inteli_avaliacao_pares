# 📧 Configuração do Sistema de Email

## 🚀 Configuração do Gmail

### 1. Ativar Verificação em 2 Etapas
1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá em "Segurança"
3. Ative "Verificação em 2 etapas"

### 2. Gerar Senha de App
1. Ainda em "Segurança"
2. Clique em "Senhas de app"
3. Selecione "Email" como aplicativo
4. Clique em "Gerar"
5. **Copie a senha gerada** (16 caracteres)

### 3. Configurar Arquivo de Configuração
Edite o arquivo `config/email_config.json`:

```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "SEU_EMAIL@gmail.com",
    "sender_password": "SUA_SENHA_DE_APP_16_CARACTERES",
    "use_tls": true,
    "app_name": "Sistema de Avaliação de Pares"
}
```

**⚠️ IMPORTANTE:**
- Use sua senha de app, NÃO sua senha normal do Gmail
- A senha de app tem 16 caracteres
- Mantenha este arquivo seguro e não compartilhe

## 🔧 Configuração Alternativa (Variáveis de Ambiente)

Se preferir usar variáveis de ambiente, crie um arquivo `.env`:

```bash
EMAIL_SENDER=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app
```

## 🧪 Testando a Configuração

### 1. Teste de Conexão
```python
from src.utils.email_service import EmailService

email_service = EmailService()
success, message = email_service.testar_conexao()
print(f"Teste: {message}")
```

### 2. Teste de Envio
```python
# Dados de teste
avaliacoes_teste = {
    'sprint': 'Sprint 2',
    'grupo': 'Grupo 1',
    'avaliacoes': [
        {
            'aluno_avaliado': 'João Silva',
            'nota_eixo1': 3,
            'nota_eixo2': 2,
            'nota_eixo3': 4,
            'feedback_eixo1': 'Excelente colaboração',
            'feedback_eixo2': 'Boa qualidade de entrega',
            'feedback_eixo3': 'Comunicação efetiva'
        }
    ]
}

# Enviar email de teste
success, message = email_service.enviar_avaliacoes(
    'destinatario@exemplo.com',
    'Nome do Usuário',
    avaliacoes_teste
)
print(f"Envio: {message}")
```

## 📱 Como Usar no Sistema

### 1. Acessar Avaliações
- Faça login no sistema
- Navegue para a tela de avaliações
- Preencha as avaliações dos colegas

### 2. Envio Automático de Email
- Após salvar as avaliações, o email é enviado automaticamente
- O sistema usa o email do usuário logado
- Confirmação aparece na mensagem de sucesso

### 3. Verificar Email
- Verifique sua caixa de entrada
- O email terá um design responsivo e profissional
- Todas as avaliações estarão organizadas por eixo

## 🎨 Personalização do Email

### Cores e Estilo
O email usa um design moderno com:
- **Header**: Gradiente azul-roxo
- **Notas**: Verde com fundo claro
- **Feedbacks**: Laranja com fundo claro
- **Layout**: Responsivo para mobile e desktop

### Conteúdo
- Nome do usuário
- Sprint e grupo
- Avaliações organizadas por eixo
- Notas e feedbacks
- Informações importantes no rodapé

## 🔒 Segurança

### Boas Práticas
1. **Nunca compartilhe** o arquivo de configuração
2. **Use senhas de app** em vez de senhas normais
3. **Mantenha atualizado** o sistema
4. **Monitore logs** de envio

### Logs de Auditoria
O sistema registra:
- Tentativas de envio
- Sucessos e falhas
- Destinatários
- Timestamps

## 🚨 Solução de Problemas

### Erro: "Erro na conexão SMTP"
- Verifique se a verificação em 2 etapas está ativa
- Confirme se a senha de app está correta
- Teste a conexão com `testar_conexao()`

### Erro: "Email não enviado"
- Verifique se o email de destino está correto
- Confirme se há avaliações para enviar
- Verifique os logs de erro

### Email não chega
- Verifique a pasta de spam
- Confirme se o email de destino está correto
- Teste com um email diferente

## 📞 Suporte

Em caso de problemas:
1. Verifique a configuração
2. Teste a conexão SMTP
3. Consulte os logs de erro
4. Entre em contato com o Professor Orientador

---

**✅ Sistema configurado e funcionando!**
