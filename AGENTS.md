# AGENTS.md

> Este arquivo orienta agentes de IA (Claude, Cursor, Copilot, etc.) trabalhando neste repositório.
> Leia por completo antes de executar qualquer tarefa.

## Idioma

**Toda documentação do projeto deve ser escrita em português (pt-BR)**: README.md, registro de decisões técnicas, documentação de arquitetura, comentários de commit relevantes e este próprio arquivo. Código (nomes de variáveis, funções, classes) permanece em inglês, seguindo convenção internacional.

## Contexto do projeto

Landing page de vendas de figurinhas/cartas do universo **Gwent (The Witcher 3)**, com captura de leads via formulário público e um CRM simples (kanban) em área autenticada para o time de vendas gerenciar esses leads.

Regra de negócio central: todo lead enviado pelo formulário público vira um card automático na coluna "Sem Contato" do kanban, atribuído a um vendedor via distribuição round robin entre 5 vendedores fixos (Marcelo, Rafael, Renato, Pedro, Leonardo).

## Stack

- **Frontend**: Vue 3 (Composition API) + Vite + Pinia (gerenciamento de estado) — deploy no Vercel
- **Backend**: FastAPI (Python) + SQLModel/SQLAlchemy — deploy no Railway
- **Banco**: PostgreSQL (produção)
- **Catálogo de figurinhas**: JSON estático em `/frontend/src/data/figurinhas.json`, importado diretamente no frontend. Não há endpoint de API nem tabela no banco para figurinhas.
- **Imagens das figurinhas**: arquivos estáticos em `/frontend/public/cards`, servidos pelo próprio frontend.
- **Estrutura**: monorepo (`/frontend` + `/backend`) em um único repositório, orquestrado via `docker-compose.yml` na raiz.

Não sugerir troca de stack, framework ou banco sem que eu peça explicitamente.

## Estrutura de pastas esperada

```
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
│   │   ├── data/          # catálogo estático de figurinhas
│   │   ├── views/
│   │   ├── stores/        # Pinia, um store por domínio (leads, auth, kanban)
│   │   ├── router/
│   │   └── services/      # chamadas à API
│   └── public/cards/      # imagens estáticas das figurinhas
└── backend/
    ├── app/
    │   ├── models/
    │   ├── routers/
    │   ├── schemas/
    │   └── services/       # lógica de negócio (ex: round robin)
    ├── migrations/
    └── tests/
```

Não inventar estrutura alternativa sem justificar no `docs/decisoes-tecnicas.md`.

## Convenções de código

- **Backend (Python)**: snake_case para variáveis/funções, PascalCase para classes. Tipagem obrigatória (type hints) em todas as funções públicas. Validação de entrada via Pydantic/SQLModel.
- **Frontend (Vue)**: Composition API com `<script setup>`. camelCase para variáveis/funções, PascalCase para componentes. Um store Pinia por domínio, tipado.
- **Commits**: mensagens em português, formato `tipo: descrição curta` (ex: `feat: adiciona endpoint de criação de lead`).
- Evitar abstrações prematuras. Priorizar clareza sobre "esperteza".

## Regra de negócio crítica — não alterar sem aviso

O algoritmo de round robin deve ser determinístico e sobreviver a reinícios do servidor (persistido em banco, não em memória). A ordem fixa é:

```
Marcelo → Rafael → Renato → Pedro → Leonardo → Marcelo → ...
```

Qualquer mudança nessa lógica, no schema de `Lead`/`Vendedor`, ou na forma de persistência do índice do round robin deve ser discutida comigo antes de implementada.

## O que o agente PODE fazer sem perguntar

- Criar/ajustar componentes visuais e estilos
- Escrever testes automatizados
- Refatorar código já aprovado para melhorar legibilidade (sem mudar comportamento)
- Sugerir melhorias de UX na landing page
- Escrever ou atualizar documentação em `docs/`

## O que o agente NÃO PODE fazer sem perguntar

- Trocar stack, framework ou biblioteca já decidida
- Alterar o schema do banco de dados
- Modificar a lógica do round robin
- Adicionar dependências novas sem justificar a necessidade
- Criar endpoint de API ou tabela de banco para figurinhas sem discutir antes
- Remover o catálogo estático em `/frontend/src/data/figurinhas.json` ou as imagens locais em `/frontend/public/cards`

## Fluxo de trabalho esperado

Antes de implementar qualquer tarefa não trivial, descrever em poucos bullets o plano (arquivos afetados, abordagem) antes de escrever código. Para tarefas pequenas (ajuste de estilo, correção de bug simples), pode implementar direto.

## Arquivos que não devem subir ao repositório

Criar e manter um `.gitignore` na raiz cobrindo, no mínimo:

- Dependências: `node_modules/`, `__pycache__/`, `.venv/`, `*.pyc`
- Variáveis de ambiente e segredos: `.env`, `.env.local`, `.env.*.local`, chaves de API e credenciais externas
- Builds: `dist/`, `build/`, `.vite/`
- Banco local: `*.sqlite3`, `*.db`
- Arquivos de IDE/SO: `.vscode/`, `.idea/`, `.DS_Store`
- Logs: `*.log`

Nunca commitar valores reais de variáveis sensíveis (chaves de API, secret de JWT, string de conexão do banco). Sempre fornecer um `.env.example` com os nomes das variáveis e valores fictícios, para o avaliador saber o que precisa configurar.

Se em algum momento eu colar uma chave ou credencial real na conversa, alertar e sugerir que seja revogada/rotacionada antes do deploy, nunca apenas adicionar ao `.gitignore` silenciosamente.

## Como rodar localmente

```bash
docker-compose up
```

Frontend em `http://localhost:5173`, backend em `http://localhost:8000` (docs automáticos em `/docs`).
