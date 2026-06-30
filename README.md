# Vitrine de Figurinhas Kateto

Landing page de vendas de figurinhas/cartas do universo Gwent (The Witcher 3), com backend em FastAPI, frontend em Vue 3 + Vite e banco PostgreSQL.

Este scaffold inicial ainda não implementa regra de negócio. Ele apenas sobe os três serviços da stack e expõe um endpoint de saúde no backend.

## Requisitos

- Docker
- Docker Compose

## Como rodar localmente

Na raiz do repositório:

```bash
docker-compose up --build
```

Serviços disponíveis:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Documentação automática da API: `http://localhost:8000/docs`
- Banco PostgreSQL: `localhost:5432`

## Como testar

Backend:

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{"status":"ok"}
```

Frontend:

Abra `http://localhost:5173` no navegador e confirme que a página inicial carrega.

Para parar os serviços:

```bash
docker-compose down
```

