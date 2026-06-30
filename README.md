# Vitrine de Figurinhas Kateto

Landing page de vendas de figurinhas/cartas do universo Gwent (The Witcher 3), com backend em FastAPI, frontend em Vue 3 + Vite e banco PostgreSQL.

O backend expõe um endpoint de saúde e já possui a base de modelos, migrations e regra de distribuição round robin para leads.

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

### Migrations do backend

Os comandos do Alembic devem ser executados de dentro do container do backend, usando `docker-compose exec backend alembic <comando>`. Não rode esses comandos diretamente no ambiente local: a connection string usa o hostname `db`, que só é resolvido dentro da rede criada pelo Docker Compose.

Exemplo para aplicar todas as migrations pendentes:

```bash
docker-compose exec backend alembic upgrade head
```

### Novas dependências Python

Sempre que uma nova dependência Python for adicionada ao backend, faça rebuild da imagem para que o container reflita a mudança:

```bash
docker-compose up -d --build backend
```

Sem esse rebuild, o pacote pode estar listado em `backend/requirements.txt`, mas ainda não estará instalado dentro do container em execução.

## Deploy

No deploy do backend, as migrations rodam automaticamente antes do servidor subir pelo start command da imagem Docker:

```bash
python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Isso usa a variável `PORT` injetada pelo Railway em produção e cai para `8000` quando ela não estiver definida. Não é necessário rodar migrations manualmente no ambiente de produção.

Em desenvolvimento local, quando precisar aplicar migrations manualmente, use o container do backend:

```bash
docker-compose exec backend alembic upgrade head
```

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
