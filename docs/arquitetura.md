# Arquitetura

## Visão geral

O projeto é organizado como um monorepo com três serviços principais orquestrados por `docker-compose.yml`:

- `frontend`: aplicação Vue 3 com Vite e Pinia.
- `backend`: API FastAPI.
- `db`: banco PostgreSQL.

O backend expõe endpoints REST para saúde da API, login simples, criação pública de leads e gerenciamento autenticado dos cards do kanban. A regra de distribuição round robin é aplicada no backend durante a criação de cada lead.

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

## Endpoints do backend

| Método | Rota | Autenticação | Propósito |
| --- | --- | --- | --- |
| `GET` | `/health` | Não | Verificar se a API está online. |
| `POST` | `/login` | Não | Validar usuário/senha e retornar um bearer token assinado. |
| `POST` | `/leads` | Não | Criar um lead público na coluna `Sem Contato` e atribuir o próximo vendedor via round robin. |
| `GET` | `/leads` | Sim | Listar os cards do kanban, com filtro opcional por coluna via query string `column`. |
| `PATCH` | `/leads/{id}` | Sim | Mover um card para uma das colunas permitidas: `Sem Contato`, `Em Contato`, `Perdido` ou `Finalizado`. |

Os endpoints autenticados esperam o header `Authorization: Bearer <token>`. O token é gerado pelo endpoint `/login` e assinado no backend com segredo configurável por variável de ambiente.
