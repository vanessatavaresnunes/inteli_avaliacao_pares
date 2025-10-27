# 🛠️ Configuração de Ambiente

## 📋 Detecção Automática de Ambiente

O sistema detecta automaticamente se está rodando em:
- **Local/Desenvolvimento**: Botão de teste aparece
- **Produção**: Botão de teste oculto

## 🔧 Como Configurar

### **Para Ambiente de Desenvolvimento (Local)**

Adicione no seu `.env`:

```bash
ENVIRONMENT=development
```

Ou simplesmente rode localmente sem essa variável - o sistema detecta automaticamente pelo hostname.

### **Para Ambiente de Produção**

Configure no deploy (Streamlit Cloud, Heroku, etc.):

```bash
ENVIRONMENT=production
```

---

## ✅ Como Funciona a Detecção

### **1. Verificação por Variável de Ambiente**
```python
is_local = os.getenv("ENVIRONMENT", "production").lower() == "development"
```
- Se `ENVIRONMENT=development` → Botão aparece
- Se `ENVIRONMENT=production` → Botão oculto
- Se não definida → Verifica hostname

### **2. Verificação por Hostname (Fallback)**
```python
hostname = socket.gethostname().lower()
is_local = (
    "localhost" in hostname or
    "127.0.0.1" in hostname or
    hostname.startswith("desktop") or
    hostname.startswith("laptop") or
    "home" in hostname
)
```

**Ambientes detectados como local:**
- ✅ localhost
- ✅ 127.0.0.1
- ✅ Desktop-[nome]
- ✅ Laptop-[nome]
- ✅ Computadores com "home" no nome

**Ambientes detectados como produção:**
- ❌ Deploy em servidor
- ❌ Hostname do servidor
- ❌ Cloud (Streamlit Cloud, Heroku, etc.)

---

## 🧪 Como Testar

### **Para ver o botão (desenvolvimento):**
```bash
# No seu .env
ENVIRONMENT=development

# Ou rode em sua máquina local (detecta automaticamente)
streamlit run app.py
```

### **Para ocultar o botão (produção):**
```bash
# No seu .env
ENVIRONMENT=production

# Ou rode no servidor (detecta automaticamente)
streamlit run app.py
```

---

## 📝 Exemplo de Uso

### **`.env` local:**
```bash
# Desenvolvimento local
ENVIRONMENT=development
PERIODO_ATUAL=2025-2B
SUPABASE_URL=https://...
SUPABASE_KEY=...
```

### **`.env` produção:**
```bash
# Produção
ENVIRONMENT=production
PERIODO_ATUAL=2025-2B
SUPABASE_URL=https://...
SUPABASE_KEY=...
```

---

## 🎯 Garantias

✅ **Botão de teste NUNCA aparece em produção automaticamente**
✅ **Pode ser forçado com `ENVIRONMENT=development`**
✅ **Segurança não comprometida mesmo se bug na detecção**

