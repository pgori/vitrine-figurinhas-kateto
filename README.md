# Vitrine de Figurinhas Kateto

Landing page fictícia de vendas de figurinhas/cartas do universo Gwent (The Witcher 3), com vitrine pública, formulário de captura de leads e área autenticada com kanban para o time de vendas.

Todo lead enviado pelo formulário público vira automaticamente um card na coluna "Sem Contato" e recebe um vendedor por distribuição round robin entre Marcelo, Rafael, Renato, Pedro e Leonardo.

## Stack

- Frontend: Vue 3 + Vite + Pinia, com deploy previsto na Vercel
- Backend: FastAPI + SQLModel/SQLAlchemy + Alembic, com deploy previsto no Railway
- Banco de dados: PostgreSQL
- Catálogo de figurinhas: JSON estático em `frontend/src/data/figurinhas.json`
- Imagens: arquivos estáticos em `frontend/public/cards`
- Orquestração local: `docker-compose.yml`

## Requisitos

- Docker
- Docker Compose

## Variáveis de ambiente

Use o arquivo `.env.example` como referência. Ele contém apenas valores fictícios/de desenvolvimento; não commit valores reais de produção.

| Variável | Serviço | Descrição |
| --- | --- | --- |
| `POSTGRES_DB` | Banco | Nome do banco PostgreSQL criado pelo Docker Compose. |
| `POSTGRES_USER` | Banco | Usuário do PostgreSQL local. |
| `POSTGRES_PASSWORD` | Banco | Senha do PostgreSQL local. |
| `DATABASE_URL` | Backend | String de conexão usada pelo FastAPI/Alembic. No Docker Compose, usa o hostname `db`. |
| `VITE_API_BASE_URL` | Frontend | URL base da API consumida pelo Vue. |
| `BACKEND_AUTH_USERNAME` | Backend | Usuário único da área autenticada. |
| `BACKEND_AUTH_PASSWORD` | Backend | Senha do usuário único da área autenticada. |
| `BACKEND_TOKEN_SECRET` | Backend | Segredo usado para assinar os tokens de autenticação. Em produção, deve ser forte e único. |
| `BACKEND_TOKEN_TTL_SECONDS` | Backend | Tempo de validade do token, em segundos. |
| `CORS_ALLOW_ORIGINS` | Backend | Lista de origens permitidas pelo CORS, separadas por vírgula. |

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

URLs de produção:

- Frontend (Vercel): preencher com a URL publicada no Vercel
- Backend (Railway): preencher com a URL pública do serviço no Railway

No deploy do backend, as migrations rodam automaticamente antes do servidor subir pelo start command da imagem Docker:

```bash
python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Isso usa a variável `PORT` injetada pelo Railway em produção e cai para `8000` quando ela não estiver definida. Não é necessário rodar migrations manualmente no ambiente de produção.

Em desenvolvimento local, quando precisar aplicar migrations manualmente, use o container do backend:

```bash
docker-compose exec backend alembic upgrade head
```

No deploy do frontend na Vercel, o arquivo `frontend/vercel.json` configura um rewrite de todas as rotas para `index.html`. Isso é necessário para o Vue Router funcionar em produção: sem esse arquivo, acessar rotas diretamente pela URL, como `/login` ou `/kanban`, retornaria 404 porque a Vercel tentaria localizar um arquivo físico para a rota.

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

Testes automatizados do backend:

```bash
cd backend
pytest -vv
```

Para parar os serviços:

```bash
docker-compose down
```

## Créditos e Aviso Legal

As imagens utilizadas neste projeto pertencem à CD Projekt Red (Gwent: The Witcher Card Game) e foram obtidas em gwent.one. Este projeto foi desenvolvido exclusivamente para fins educacionais como parte de um processo seletivo, sem qualquer intenção comercial.
