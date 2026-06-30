# Arquitetura

## Visão geral

O projeto é organizado como um monorepo com três serviços principais orquestrados por `docker-compose.yml`:

- `frontend`: aplicação Vue 3 com Vite e Pinia.
- `backend`: API FastAPI.
- `db`: banco PostgreSQL.

Neste scaffold inicial, a aplicação ainda não possui lógica de negócio, autenticação, modelos de banco ou integração com Cloudflare R2. O backend expõe apenas `GET /health` para validar que o serviço está online, e o frontend possui uma página inicial mínima para validar o carregamento do Vite.

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

