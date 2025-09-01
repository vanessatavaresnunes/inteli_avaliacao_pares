# 🚀 Instruções de Execução - Sistema de Avaliação de Pares

## Pré-requisitos

- Python 3.7+
- Streamlit 1.28.0+
- Todas as dependências listadas em `requirements.txt`

## 📋 Passos para Execução

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o Aplicativo
```bash
streamlit run app.py
```

### 3. Acessar no Navegador
O aplicativo será aberto automaticamente em: `http://localhost:8501`

## 🔐 Primeiro Acesso

### Opção 1: Usar Usuários de Teste
- **Email**: `aluno.teste@sou.inteli.edu.br` (alunos) ou `professor.teste@prof.inteli.edu.br` (professores)
- **Senha**: `123456`
- **Turma**: T13
- **Grupo**: Grupo 1

### Opção 2: Criar Novo Cadastro
1. Clique em "📝 Novo Cadastro"
2. Preencha suas informações:
   - Email institucional (@sou.inteli.edu.br ou @prof.inteli.edu.br)
   - Nome completo
   - Senha (mínimo 6 caracteres)
   - Turma (T09-T20)
   - Grupo (disponível para sua turma)
3. Clique em "🚀 Criar Conta"

## 🎯 Funcionalidades Disponíveis

### ✅ Sistema de Login
- Autenticação com email institucional
- Senhas criptografadas com bcrypt
- Validação de formato de email

### ✅ Cadastro de Usuários
- Validação de dados em tempo real
- Seleção de turma e grupo
- Verificação de usuário existente

### ✅ Redefinição de Senha
- Recuperação por email institucional
- Validação de usuário existente
- Nova senha com confirmação

### ✅ Redirecionamento Automático
- Após login, usuário vai direto para sua turma/grupo
- Acesso direto às avaliações específicas
- Interface personalizada por usuário

### ✅ Sistema de Avaliação
- Seleção de sprint (1-5)
- Avaliação por eixos
- Validação de notas e feedbacks
- Salvamento seguro das avaliações

## 🛠️ Estrutura de Arquivos

```
📁 Projeto/
├── 📄 app.py                          # Aplicativo principal
├── 📁 src/
│   ├── 📁 views/                      # Telas de interface
│   │   ├── 📄 login_view_new.py       # Tela de login
│   │   ├── 📄 cadastro_view_new.py    # Tela de cadastro
│   │   └── 📄 password_reset_view.py  # Tela de redefinição de senha
│   ├── 📁 utils/                      # Utilitários
│   │   └── 📄 user_storage.py         # Gerenciamento de usuários
│   └── 📁 controllers/                # Controladores
│       └── 📄 avaliacao_controller.py # Controller de avaliações
├── 📁 data/                           # Dados do sistema
│   ├── 📁 usuarios/                   # Usuários cadastrados
│   │   └── 📄 usuarios.json           # Arquivo de usuários
│   └── 📄 turmas_config.json         # Configuração de turmas
└── 📄 requirements.txt                 # Dependências Python
```

## 🔧 Configurações

### Turmas e Grupos
As turmas disponíveis são configuradas em `data/turmas_config.json`:
- **Turmas**: T09 a T20
- **Grupos**: Variam por turma (ex: T13 tem 5 grupos)

### Usuários
Os usuários são armazenados em `data/usuarios/usuarios.json`:
- Senhas criptografadas com bcrypt
- Informações de turma e grupo
- Timestamp de criação

## 🚨 Solução de Problemas

### Erro de Importação
```bash
# Verificar se o Python está no PATH
python --version

# Verificar se as dependências estão instaladas
pip list | grep streamlit
pip list | grep bcrypt
```

### Erro de Permissão
```bash
# No Windows, executar como administrador
# No Linux/Mac, verificar permissões de arquivo
chmod +x app.py
```

### Porta Ocupada
```bash
# Usar porta diferente
streamlit run app.py --server.port 8502
```

## 📱 Interface do Usuário

### Tela de Login
- Formulário de email e senha
- Botões para cadastro e redefinição de senha
- Validação em tempo real

### Tela de Cadastro
- Formulário completo de informações
- Seleção de turma e grupo
- Validações visuais

### Tela de Avaliação
- Seleção de sprint
- Matriz de avaliação por eixos
- Validação de dados
- Botão de salvar

## 🔒 Segurança

- **Senhas**: Criptografadas com bcrypt
- **Emails**: Apenas institucionais (@sou.inteli.edu.br para alunos, @prof.inteli.edu.br para professores)
- **Sessão**: Gerenciada pelo Streamlit
- **Dados**: Armazenados localmente em JSON

## 📊 Monitoramento

### Logs do Sistema
- Verificar console do terminal
- Mensagens de erro e sucesso
- Validações de dados

### Arquivos de Dados
- `data/usuarios/usuarios.json`: Usuários cadastrados
- `data/avaliacoes/`: Avaliações salvas
- `data/alunos.json`: Dados dos alunos organizados por turma e grupo

## 🎉 Sucesso!

Após executar todos os passos, você terá:
- ✅ Sistema de login funcional
- ✅ Cadastro de usuários
- ✅ Redefinição de senhas
- ✅ Redirecionamento automático
- ✅ Sistema de avaliação integrado
- ✅ Interface moderna e responsiva

**Bom uso do sistema! 🚀**

