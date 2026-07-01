# Arquitetura

Este documento descreve o que existe no projeto hoje e como as peças se conectam. As motivações das escolhas técnicas estão registradas em `docs/decisoes-tecnicas.md`.

## 1. Visão geral do sistema

```text
┌─────────┐      ┌────────────────────┐      ┌────────────────────┐      ┌────────────────────┐
│ Browser │ ───> │ Frontend / Vercel  │ ───> │ Backend / Railway  │ ───> │ Railway Postgres   │
└─────────┘      └────────────────────┘      └────────────────────┘      └────────────────────┘
                      Vue 3 + Vite              FastAPI + Alembic              PostgreSQL
```

- Browser: acessa a vitrine pública, o formulário de compra, o login e o kanban.
- Frontend: renderiza a aplicação Vue, carrega o catálogo estático e chama a API.
- Backend: valida dados, autentica usuários, cria leads, distribui vendedores e move cards.
- Banco: persiste vendedores, leads e o estado do round robin.

Localmente, os três serviços são orquestrados pelo `docker-compose.yml`: `frontend`, `backend` e `db`.

## 2. Frontend

O frontend fica em `frontend/` e usa Vue 3, Vite, Vue Router e Pinia.

### Páginas

| Rota | Arquivo | Responsabilidade |
| --- | --- | --- |
| `/` | `src/views/HomeView.vue` | Landing page e vitrine de figurinhas. Lê o catálogo estático, exibe os cards e inicia o fluxo de compra. |
| `/comprar` | `src/views/ComprarView.vue` | Overlay de compra. Lê o item selecionado via query string `item`, mostra a figurinha e renderiza o formulário público. |
| `/login` | `src/views/LoginView.vue` | Tela de autenticação da área interna. Envia usuário/senha para o backend e redireciona para `/kanban` em caso de sucesso. |
| `/kanban` | `src/views/KanbanView.vue` | Área autenticada do CRM. Lista leads em quatro colunas e permite movimentação por drag and drop. |

O Vue Router usa `createWebHistory()`. A rota `/kanban` exige autenticação; sem token, o usuário é redirecionado para `/login`. A rota `/login` é marcada como `guestOnly`; se o usuário já estiver autenticado, ele vai direto para `/kanban`.

### Stores Pinia

| Store | Arquivo | Estado gerenciado |
| --- | --- | --- |
| `auth` | `src/stores/auth.js` | Token, loading do login, mensagem de erro, login e logout. |
| `leads` | `src/stores/leads.js` | Estado do formulário público, figurinha selecionada, loading do envio, mensagens de sucesso/erro, lead criado e posição de scroll da vitrine. |
| `kanban` | `src/stores/kanban.js` | Leads agrupados por coluna, loading, erro, snapshot de drag and drop e movimentação otimista de cards. |

### Catálogo e imagens

O catálogo de figurinhas é carregado diretamente de `src/data/figurinhas.json`. Não existe endpoint de API nem tabela de banco para figurinhas.

As imagens são assets estáticos servidos pelo frontend em `frontend/public/cards`. Essa decisão está detalhada no item 5 de `docs/decisoes-tecnicas.md`.

### Autenticação no frontend

O token retornado por `POST /login` é salvo no store `auth` e também em `localStorage` pela camada `src/services/api.js`. Ao inicializar, o store lê o token salvo para manter a sessão após reload da página.

As chamadas autenticadas passam pelo mesmo `api.js`, que injeta `Authorization: Bearer <token>` quando a requisição exige autenticação.

### Kanban e drag and drop

O kanban usa `vuedraggable` (`vuedraggable@4.1.0`), baseado em SortableJS. Cada coluna é renderizada por `src/components/KanbanColuna.vue`, e cada lead por `src/components/KanbanCard.vue`.

As colunas fixas são:

1. `Sem Contato`
2. `Em Contato`
3. `Perdido`
4. `Finalizado`

Ao mover um card, o store `kanban` atualiza a interface de forma otimista e chama `PATCH /leads/{id}`. Se o backend retornar erro, o snapshot anterior é restaurado.

## 3. Backend

O backend fica em `backend/` e usa FastAPI, SQLModel/SQLAlchemy, Pydantic e Alembic.

### Tabelas e relacionamentos

| Tabela | Modelo | Campos principais | Relacionamentos |
| --- | --- | --- | --- |
| `sellers` | `Seller` | `id`, `name`, `queue_order`, `created_at`, `updated_at` | Um vendedor pode ter muitos leads. |
| `leads` | `Lead` | `id`, `name`, `desired_item`, `phone`, `kanban_column`, `assigned_seller_id`, `created_at`, `updated_at` | Cada lead pertence a um vendedor via `assigned_seller_id`. |
| `round_robin_state` | `RoundRobinState` | `id`, `next_seller_order`, `updated_at` | Tabela singleton usada para persistir o próximo vendedor da fila. |

A migration `20260630_0001_create_sales_models.py` cria as três tabelas, o índice em `leads.assigned_seller_id`, os vendedores iniciais e o registro inicial do round robin.

Os vendedores semeados são:

```text
Marcelo -> Rafael -> Renato -> Pedro -> Leonardo
```

### Endpoints

| Método | Rota | Autenticação | Propósito |
| --- | --- | --- | --- |
| `GET` | `/health` | Não | Verificar se a API está online. |
| `POST` | `/login` | Não | Validar usuário/senha e retornar um bearer token. |
| `POST` | `/leads` | Não | Criar um lead público em `Sem Contato` e atribuir vendedor via round robin. |
| `GET` | `/leads` | Sim | Listar cards do kanban. Aceita filtro opcional `column`. |
| `PATCH` | `/leads/{id}` | Sim | Mover um lead para uma das quatro colunas permitidas. |

Os schemas de request/response ficam em `backend/app/schemas/`. A API converte erros de validação do FastAPI para status `400`.

### Round robin

A criação de lead passa por `create_lead_with_round_robin()` em `backend/app/services/lead_assignment.py`.

O fluxo é:

1. Inicia uma transação.
2. Lê o registro singleton `round_robin_state` com lock.
3. Busca o vendedor cujo `queue_order` é igual a `next_seller_order`.
4. Cria o lead na coluna `Sem Contato` com `assigned_seller_id`.
5. Atualiza `next_seller_order` para o próximo vendedor da fila.
6. Faz commit da transação.

O estado fica persistido em banco, então a fila não reinicia quando o servidor reinicia. A abordagem de lock e concorrência está detalhada no item 6 de `docs/decisoes-tecnicas.md`.

### Autenticação

A autenticação está em `backend/app/services/auth.py`.

O projeto usa um bearer token assinado pelo backend. Ele contém um payload base64url com:

- `sub`: usuário autenticado;
- `exp`: timestamp de expiração.

A assinatura usa HMAC-SHA256 com `BACKEND_TOKEN_SECRET`. O tempo de validade vem de `BACKEND_TOKEN_TTL_SECONDS`. As credenciais simples de login vêm de `BACKEND_AUTH_USERNAME` e `BACKEND_AUTH_PASSWORD`.

Endpoints protegidos usam `HTTPBearer` e a dependência `get_current_user()`. Se o header estiver ausente, a API retorna `401`; se o token for inválido ou expirado, retorna `403`.

## 4. Fluxos principais

### Fluxo de compra

```text
Usuário clica em "Quero essa"
-> frontend navega para /comprar?item=<id>
-> ComprarView localiza a figurinha no JSON
-> formulário envia nome, item desejado e telefone
-> POST /leads
-> backend valida os dados
-> backend atribui vendedor via round robin
-> lead é salvo em "Sem Contato"
-> frontend exibe mensagem de confirmação
-> card fica disponível no kanban
```

O formulário aplica máscara visual no telefone, mas envia apenas dígitos para o backend. Durante o envio, o botão mostra `Enviando...` e fica desabilitado. Em erro, o formulário exibe a mensagem retornada pela API sem limpar os campos.

### Fluxo do kanban

```text
Usuário acessa /login
-> POST /login
-> token salvo no Pinia e no localStorage
-> navegação para /kanban
-> store kanban busca GET /leads?column=<coluna> para cada coluna
-> usuário arrasta um card para outra coluna
-> frontend atualiza o estado local de forma otimista
-> PATCH /leads/{id}
-> backend persiste a nova coluna
-> em erro, frontend restaura o snapshot anterior
```

## 5. Decisões de infraestrutura

### Desenvolvimento local

O `docker-compose.yml` sobe:

- `db`: PostgreSQL 16 Alpine;
- `backend`: FastAPI em `http://localhost:8000`;
- `frontend`: Vite em `http://localhost:5173`.

As migrations manuais devem ser executadas dentro do container do backend:

```bash
docker-compose exec backend alembic upgrade head
```

### Deploy

O frontend está preparado para Vercel. O arquivo `frontend/vercel.json` redireciona todas as rotas para `index.html`, permitindo que o Vue Router controle rotas como `/login` e `/kanban`.

O backend está preparado para Railway via `backend/Dockerfile`. O comando de inicialização roda migrations antes do servidor:

```bash
python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Em produção, o backend usa a variável `PORT` injetada pelo Railway e o banco PostgreSQL configurado por `DATABASE_URL`.

### Variáveis de ambiente

As variáveis esperadas estão exemplificadas em `.env.example`:

| Variável | Uso |
| --- | --- |
| `POSTGRES_DB` | Nome do banco local no Docker Compose. |
| `POSTGRES_USER` | Usuário local do PostgreSQL. |
| `POSTGRES_PASSWORD` | Senha local do PostgreSQL. |
| `DATABASE_URL` | Conexão usada pelo backend e pelo Alembic. |
| `VITE_API_BASE_URL` | URL base da API consumida pelo frontend. |
| `BACKEND_AUTH_USERNAME` | Usuário da área autenticada. |
| `BACKEND_AUTH_PASSWORD` | Senha da área autenticada. |
| `BACKEND_TOKEN_SECRET` | Segredo de assinatura dos tokens. |
| `BACKEND_TOKEN_TTL_SECONDS` | Tempo de validade dos tokens. |
| `CORS_ALLOW_ORIGINS` | Origens permitidas pelo CORS. |

### Assets estáticos

As imagens das figurinhas ficam em `frontend/public/cards` e são servidas pelo próprio frontend. O backend não participa da entrega dessas imagens.
