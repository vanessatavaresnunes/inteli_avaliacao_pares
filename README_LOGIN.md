# Sistema de Login e Cadastro - Avaliação de Pares

## Visão Geral

Este sistema implementa um fluxo completo de autenticação para o Sistema de Avaliação de Pares, permitindo que alunos se cadastrem e façam login para acessar suas avaliações específicas por turma e grupo.

## Funcionalidades

### 🔐 Login
- **Email institucional**: Apenas emails @sou.inteli.edu.br (alunos) e @prof.inteli.edu.br (professores) são aceitos
- **Senha**: Sistema de autenticação seguro com senhas criptografadas
- **Redirecionamento automático**: Após login, o usuário é direcionado diretamente para sua turma e grupo

### 📝 Cadastro
- **Validação de email**: Verifica se é um email institucional válido
- **Seleção de turma**: Escolha entre T09 a T20
- **Seleção de grupo**: Grupos disponíveis variam por turma
- **Validação de senha**: Mínimo 6 caracteres com confirmação
- **Armazenamento seguro**: Senhas são criptografadas usando bcrypt

### 🔑 Redefinição de Senha
- **Recuperação por email**: Usuários podem redefinir suas senhas
- **Validação de usuário**: Verifica se o usuário existe antes de permitir alteração

## Estrutura de Arquivos

```
src/
├── utils/
│   └── user_storage.py          # Gerenciamento de usuários
├── views/
│   ├── login_view_new.py        # Tela de login
│   ├── cadastro_view_new.py     # Tela de cadastro
│   └── password_reset_view.py   # Tela de redefinição de senha
└── controllers/
    └── avaliacao_controller.py  # Controller com método configurar_turma_grupo

data/
├── usuarios/
│   └── usuarios.json            # Arquivo de usuários cadastrados
└── turmas_config.json           # Configuração de turmas e grupos
```

## Como Usar

### 1. Primeiro Acesso
1. Acesse o sistema
2. Clique em "📝 Novo Cadastro"
3. Preencha suas informações:
   - Email institucional (@sou.inteli.edu.br ou @prof.inteli.edu.br)
   - Nome completo
   - Senha (mínimo 6 caracteres)
   - Turma (T09-T20)
   - Grupo (disponível para sua turma)
4. Clique em "🚀 Criar Conta"

### 2. Login
1. Digite seu email institucional
2. Digite sua senha
3. Clique em "🚀 Entrar"
4. Você será redirecionado automaticamente para sua turma/grupo

### 3. Redefinir Senha
1. Na tela de login, clique em "🔑 Esqueci a Senha"
2. Digite seu email institucional
3. Digite e confirme a nova senha
4. Clique em "🔑 Atualizar Senha"

## Usuários de Teste

Para testar o sistema, foram criados usuários de exemplo:

- **Email**: `aluno.teste@sou.inteli.edu.br`
- **Senha**: `123456`
- **Turma**: T13
- **Grupo**: Grupo 1

- **Email**: `professor.teste@prof.inteli.edu.br`
- **Senha**: `123456`
- **Turma**: T13
- **Grupo**: Grupo 2

- **Email**: `teste@sou.inteli.edu.br`
- **Senha**: `nova_senha456`
- **Turma**: T13
- **Grupo**: Grupo 1

## Segurança

- **Senhas criptografadas**: Todas as senhas são hasheadas usando bcrypt
- **Validação de email**: Apenas emails institucionais são aceitos
- **Armazenamento local**: Dados são armazenados em arquivos JSON locais
- **Sessão segura**: Informações do usuário são mantidas na sessão do Streamlit

## Configuração de Turmas

As turmas e grupos disponíveis são configurados no arquivo `data/turmas_config.json`. Para adicionar novas turmas ou modificar grupos existentes, edite este arquivo.

## Dependências

- `streamlit`: Interface web
- `bcrypt`: Criptografia de senhas
- `json`: Manipulação de arquivos JSON
- `pathlib`: Manipulação de caminhos de arquivo

## Execução

Para executar o sistema:

```bash
streamlit run app.py
```

O sistema irá:
1. Mostrar a tela de login
2. Permitir cadastro de novos usuários
3. Autenticar usuários existentes
4. Redirecionar para a avaliação específica da turma/grupo
5. Manter sessão ativa até logout

## Fluxo de Navegação

```
Login → [Cadastro] → [Redefinir Senha]
  ↓
Autenticação → Redirecionamento para Turma/Grupo → Avaliação
  ↓
Logout → Retorno ao Login
```
