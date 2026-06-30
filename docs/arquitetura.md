# Arquitetura

## Visão geral

O projeto é organizado como um monorepo com três serviços principais orquestrados por `docker-compose.yml`:

- `frontend`: aplicação Vue 3 com Vite e Pinia.
- `backend`: API FastAPI.
- `db`: banco PostgreSQL.

O backend expõe endpoints REST para saúde da API, login simples, criação pública de leads e gerenciamento autenticado dos cards do kanban. A regra de distribuição round robin é aplicada no backend durante a criação de cada lead.

O frontend possui duas áreas:
- área pública, com landing page, vitrine de figurinhas e formulário de compra;
- área autenticada, com login e kanban para gestão dos leads.

## Estrutura

```text
/
├── docker-compose.yml
├── README.md
├── AGENTS.md
├── docs/
│   ├── arquitetura.md
│   └── decisoes-tecnicas.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── data/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── router/
│   │   └── services/
│   └── public/cards/
└── backend/
    ├── app/
    │   ├── models/
    │   ├── routers/
    │   ├── schemas/
    │   └── services/
    ├── migrations/
    └── tests/
```

## Serviços locais

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger/OpenAPI: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

## Catálogo de figurinhas

O catálogo de figurinhas é estático e fica em `frontend/src/data/figurinhas.json`, sendo importado diretamente pelo frontend. As imagens ficam em `frontend/public/cards`.

Não há endpoint de API nem tabela de banco para esse catálogo. O backend permanece responsável por leads, autenticação e movimentação dos cards do kanban.

## Endpoints do backend

| Método | Rota | Autenticação | Propósito |
| --- | --- | --- | --- |
| `GET` | `/health` | Não | Verificar se a API está online. |
| `POST` | `/login` | Não | Validar usuário/senha e retornar um bearer token assinado. |
| `POST` | `/leads` | Não | Criar um lead público na coluna `Sem Contato` e atribuir o próximo vendedor via round robin. |
| `GET` | `/leads` | Sim | Listar os cards do kanban, com filtro opcional por coluna via query string `column`. |
| `PATCH` | `/leads/{id}` | Sim | Mover um card para uma das colunas permitidas: `Sem Contato`, `Em Contato`, `Perdido` ou `Finalizado`. |

Os endpoints autenticados esperam o header `Authorization: Bearer <token>`. O token é gerado pelo endpoint `/login` e assinado no backend com segredo configurável por variável de ambiente.

## Fluxo de autenticação no frontend

A página `/login` envia usuário e senha para `POST /login`. Quando o backend retorna sucesso, o token é salvo no store Pinia `auth` e persistido em `localStorage`, permitindo que o usuário continue autenticado após reload da página.

O Vue Router possui guard de navegação:
- ao acessar `/kanban` sem token no store `auth`, o usuário é redirecionado para `/login`;
- ao acessar `/login` já autenticado, o usuário é redirecionado para `/kanban`;
- o botão de logout limpa o store `auth`, remove o token do `localStorage` e volta para `/login`.

A camada `frontend/src/services/api.js` centraliza as chamadas HTTP. Nas rotas autenticadas, ela injeta o header `Authorization: Bearer <token>` usando o token salvo localmente.

## Estrutura do kanban

O kanban fica em `/kanban` e usa quatro colunas fixas, nesta ordem:

1. `Sem Contato`
2. `Em Contato`
3. `Perdido`
4. `Finalizado`

O store Pinia `kanban` carrega os leads por coluna chamando `GET /leads?column=<coluna>` e mantém os cards agrupados por status. Cada card exibe nome do lead, figurinha desejada, telefone, vendedor responsável e data de criação.

A movimentação entre colunas usa `vuedraggable`, baseado em SortableJS. Ao soltar um card em outra coluna, o frontend atualiza o estado local de forma otimista e chama `PATCH /leads/{id}` para persistir a nova coluna. Se o backend retornar erro, o store restaura o estado anterior do quadro.
