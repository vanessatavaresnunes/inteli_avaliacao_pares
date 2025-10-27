# 📦 Instruções para Configuração do Bucket 2025-2B

## ✅ Importante

Você **NÃO precisa** de credenciais separadas para o novo bucket!

O sistema usa as **mesmas credenciais do Supabase** que você já tem configuradas.

## 🎯 O Que Você Precisa Fazer

### 1. Criar o Bucket no Supabase

1. Acesse: https://app.supabase.com
2. Selecione seu projeto
3. Vá em **Storage** (menu lateral esquerdo)
4. Clique em **New bucket**
5. **Nome do bucket**: `inteli_avalpares_2025_2B`
6. **Configurações**:
   - Público: Opcional (depende se você quer arquivos públicos)
   - Políticas: Deixe o padrão ou configure conforme necessário
7. Clique em **Create bucket**

### 2. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na **raiz do projeto** com:

```bash
# Configurações do Supabase (use as mesmas credenciais antigas)
NEXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=sua-chave-publica

# Período Acadêmico Atual
PERIODO_ATUAL=2025-2B
```

**Onde encontrar as credenciais:**
- No Supabase Dashboard → Settings → API
- Na seção "Project API keys"
- Use a "anon" ou "public" key

### 3. Estrutura de Buckets

- **2025-2A**: `inteli_avaliacao_pares_sprint` (bucket antigo)
- **2025-2B**: `inteli_avalpares_2025_2B` (novo bucket a criar)

### 4. Como Mudar o Período

Para usar 2025-2B, edite o arquivo `.env`:

```bash
# Para usar 2025-2A
PERIODO_ATUAL=2025-2A

# Para usar 2025-2B
PERIODO_ATUAL=2025-2B
```

## 📝 Resumo

- ✅ **Credenciais**: Mesmas do Supabase existente
- ✅ **Novo bucket**: Criar com nome `inteli_avalpares_2025_2B`
- ✅ **Configuração**: Arquivo `.env` na raiz
- ✅ **Trocar período**: Mudar `PERIODO_ATUAL` em `.env`
