# Sobre o Projeto

Sistema completo de gerenciamento de usuários e geração de exercícios personalizados utilizando **Flask** e **Inteligência Artificial**. O projeto foi desenvolvido para atender aos requisitos da disciplina PUC-RJ, implementando uma API robusta com interface web moderna e integração com IA para personalização de exercícios.

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd mvp-backend-project-pucrj
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure variáveis de ambiente (opcional):**
```bash
# Crie um arquivo .env
echo "OPENROUTER_API_KEY=sua_chave_aqui" > .env
```

4. **Execute a aplicação:**
```bash
python app.py
```

5. **Acesse a aplicação:**
- **Frontend:** http://localhost:5000
- **Swagger UI:** http://localhost:5000/swagger

## 📖 Documentação da API

A documentação completa está disponível através do **Swagger UI** em `/swagger`. Inclui:

- ✅ Descrição detalhada de cada endpoint
- ✅ Estrutura de requisição e resposta
- ✅ Códigos de status HTTP
- ✅ Exemplos práticos de uso
- ✅ Testes interativos da API


## Objetivo

Criar uma aplicação web que permita:
- Gerenciamento completo de usuários
- Geração automática de exercícios personalizados usando IA
- Interface intuitiva e responsiva
- Documentação completa da API
- Sistema de níveis de experiência

## Funcionalidades Principais

###  Gerenciamento de Usuários
- **Cadastro de usuários** com informações completas
- **Busca de usuários** por nome
- **Listagem de usuários** com filtros
- **Exclusão de usuários** e seus dados relacionados
- **Sistema de níveis**: Iniciante, Intermediário, Avançado

### Sistema de Exercícios
- **Geração automática** de exercícios usando IA (OpenRouter)
- **Personalização** baseada no nível do usuário
- **Controle de progresso** (exercícios concluídos/pendentes)
- **Histórico completo** de exercícios por usuário
- **Fallbacks inteligentes** para garantir disponibilidade

### 📊 Estatísticas e Monitoramento
- **Dashboard de estatísticas** em tempo real
- **Métricas de uso** e engajamento
- **Distribuição por níveis** de experiência
- **Taxa de conclusão** de exercícios

## Tecnologias Utilizadas

### Backend
- **Flask 2.3.3** - Framework web Python
- **Flask-SQLAlchemy 3.0.5** - ORM para banco de dados
- **Flask-CORS 4.0.0** - CORS para requisições cross-origin
- **Flask-Swagger-UI 4.11.1** - Documentação interativa da API
- **SQLite** - Banco de dados relacional
- **httpx 0.24.1** - Cliente HTTP assíncrono
- **OpenRouter API** - Integração com modelos de IA

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilos modernos com gradientes suaves
- **JavaScript ES6+** - Lógica da aplicação
- **Bootstrap 5.1.3** - Framework CSS responsivo
- **Font Awesome 6.0.0** - Ícones

### Integração com IA
- **OpenRouter API** - Acesso a modelos de IA
- **Microsoft Phi-3-mini-4k-instruct** - Modelo principal (rápido e eficiente)
- **GPT-3.5-turbo** - Modelo de fallback
- **Cache inteligente** para otimização de performance

## 🗄️ Estrutura do Banco de Dados

### Tabela: `usuarios`
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    idade INTEGER NOT NULL,
    peso FLOAT,
    altura FLOAT,
    nivel_experiencia VARCHAR(20) NOT NULL DEFAULT 'iniciante',
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_exercicios INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT 1
);
```

### Tabela: `exercicios_personalizados`
```sql
CREATE TABLE exercicios_personalizados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    vantagens TEXT NOT NULL,
    passo_a_passo TEXT NOT NULL,
    nivel_dificuldade VARCHAR(20) NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    concluido BOOLEAN DEFAULT 0,
    data_conclusao DATETIME,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

### Índices para Performance
- `idx_usuarios_nome` - Busca rápida por nome
- `idx_exercicios_usuario_id` - Consultas por usuário
- `idx_exercicios_concluido` - Filtros de status

## 📚 API Endpoints

### 👥 Usuários

#### `POST /api/cadastrar_usuario`
Cadastra um novo usuário no sistema.

**Parâmetros:**
```json
{
    "nome": "João Silva",
    "email": "joao@email.com",
    "idade": 25,
    "peso": 70.5,
    "altura": 1.75,
    "nivel_experiencia": "iniciante"
}
```

**Resposta (201):**
```json
{
    "message": "Usuário cadastrado com sucesso",
    "usuario": {
        "id": 1,
        "nome": "João Silva",
        "email": "joao@email.com",
        "idade": 25,
        "peso": 70.5,
        "altura": 1.75,
        "nivel_experiencia": "iniciante",
        "data_cadastro": "2024-12-24T16:30:00Z",
        "total_exercicios": 0,
        "ativo": true
    }
}
```

#### `GET /api/buscar_usuario/{nome_usuario}`
Busca um usuário específico pelo nome.

**Resposta (200):**
```json
{
    "usuario": {
        "id": 1,
        "nome": "João Silva",
        "email": "joao@email.com",
        "idade": 25,
        "nivel_experiencia": "iniciante",
        "total_exercicios": 5
    },
    "estatisticas": {
        "total_exercicios": 5,
        "exercicios_concluidos": 3,
        "dias_cadastrado": 15
    }
}
```

#### `GET /api/buscar_usuarios`
Lista todos os usuários cadastrados.

**Parâmetros de Query:**
- `ativo=true` - Filtrar apenas usuários ativos
- `nivel=iniciante` - Filtrar por nível de experiência

#### `DELETE /api/deletar_usuario/{nome_usuario}`
Remove um usuário e todos os seus exercícios.

### 🏃 Exercícios

#### `POST /api/gerar_exercicio_personalizado/{nome_usuario}`
Gera um exercício personalizado usando IA.

**Parâmetros (opcional):**
```json
{
    "nome_exercicio": "Polichinelo"
}
```

**Resposta (200):**
```json
{
    "exercicio": {
        "id": 1,
        "nome": "Polichinelo",
        "descricao": "Exercício cardiovascular completo...",
        "vantagens": "Melhora condicionamento físico...",
        "passo_a_passo": "1. Posicione-se...",
        "nivel_dificuldade": "iniciante",
        "concluido": false
    },
    "mensagem": "Exercício 'Polichinelo' gerado personalizado para João Silva"
}
```

#### `GET /api/exercicios_usuario/{nome_usuario}`
Lista exercícios de um usuário específico.

**Parâmetros de Query:**
- `concluido=true` - Apenas exercícios concluídos
- `concluido=false` - Apenas exercícios pendentes

#### `PATCH /api/concluir_exercicio/{exercicio_id}`
Marca um exercício como concluído.

### 📊 Estatísticas

#### `GET /api/estatisticas`
Retorna estatísticas gerais do sistema.

**Resposta (200):**
```json
{
    "total_usuarios": 25,
    "total_exercicios": 150,
    "exercicios_concluidos": 89,
    "usuarios_por_nivel": {
        "iniciante": 12,
        "intermediario": 8,
        "avancado": 5
    }
}
```

## 🎨 Interface Web

### Características da SPA
- **Design responsivo** com Bootstrap 5
- **Navegação por abas** intuitiva
- **Cores discretas e profissionais**
- **Animações suaves** e feedback visual
- **Cards interativos** para usuários e exercícios
- **Loading spinners** e alertas informativos

### Seções da Interface

#### 1. 👥 Usuários
- **Formulário de cadastro** com validação
- **Busca por nome** com resultados detalhados
- **Lista de usuários** em cards organizados
- **Ações rápidas** (gerar exercício, deletar)

#### 2. 🏃 Exercícios
- **Geração de exercícios** com IA
- **Lista de exercícios** por usuário
- **Controle de progresso** (marcar como concluído)
- **Visualização detalhada** de cada exercício

#### 3. 📊 Estatísticas
- **Dashboard visual** com métricas
- **Gráficos de distribuição** por níveis
- **Indicadores de performance** em tempo real

#### 4. 📖 Documentação
- **Link direto** para Swagger UI
- **Lista de endpoints** disponíveis
- **Exemplos de uso** da API
- 
## 🎯 Funcionalidades Especiais

### 🤖 Integração com IA
- **Personalização inteligente** baseada no nível do usuário
- **Fallbacks automáticos** para garantir disponibilidade
- **Cache otimizado** para melhor performance
- **Múltiplos modelos** de IA (principal + fallback)

### 🎨 Sistema de Níveis
- **Iniciante:** Exercícios básicos e explicativos
- **Intermediário:** Exercícios com complexidade média
- **Avançado:** Exercícios desafiadores e intensos

### 📈 Otimizações de Performance
- **Índices de banco** para consultas rápidas
- **Cache inteligente** para exercícios populares
- **Requisições assíncronas** para IA
- **Fallbacks rápidos** em caso de timeout

## 🔒 Segurança e Validação

### Validações Implementadas
- **Email único** no cadastro
- **Campos obrigatórios** validados
- **Sanitização de entrada** nos formulários
- **Tratamento de erros** robusto

### Tratamento de Exceções
- **Rollback automático** em falhas de banco
- **Mensagens de erro** claras e informativas
- **Logs detalhados** para debugging
- **Fallbacks graciais** para serviços externos

## 📊 Métricas e Monitoramento

### Estatísticas Disponíveis
- **Total de usuários** cadastrados
- **Total de exercícios** gerados
- **Taxa de conclusão** de exercícios
- **Distribuição por níveis** de experiência
- **Métricas de uso** por usuário
- ✅ **Otimizações de performance**

O sistema está pronto para uso em ambiente de produção com os devidos ajustes de segurança e infraestrutura.
