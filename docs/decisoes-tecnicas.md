# Registro de decisões técnicas

> Este documento registra as principais decisões tomadas durante o desenvolvimento, as alternativas consideradas e o porquê de cada escolha. Atualizado conforme o projeto evolui.

## 1. Universo temático: Gwent (The Witcher 3)

**Alternativas consideradas**: UFC/MMA.

**Decisão**: Gwent.

**Motivo**: Considerei o esporte MMA, por gostar de lutas e Gwent por fazer parte de um dos meus jogos favoritos. Porém, decidi pelo Gwent pela identidade visual do jogo que já oferece um material rico para diferenciação visual da landing page, frente a temas mais comuns (futebol, e-sports tradicionais). A metáfora de "cartas colecionáveis" também mapeia naturalmente para "figurinhas", facilitando o conceito de produto.

## 2. Stack de backend: FastAPI

**Alternativas consideradas**: Django REST Framework, Flask.

**Decisão**: FastAPI.

**Motivo**: Estou mais acostumado com DRF, mas para o escopo do teste (poucos endpoints, regra de negócio central bem definida), o DRF traria overhead de configuração (serializers, viewsets, urls) desproporcional ao benefício. FastAPI oferece validação de dados nativa via Pydantic/SQLModel, tipagem forte, documentação automática (Swagger) e menor verbosidade — o que favorece legibilidade, um dos critérios avaliados.

## 3. Stack de frontend: Vue 3 + Pinia

**Alternativas consideradas**: Next.js (React).

**Decisão**: Vue 3 (Composition API) com Pinia para gerenciamento de estado.

**Motivo**: Tenho mais expertise com Vue 3. A prioridade foi maximizar produtividade e familiaridade com a ferramenta, já que a qualidade do código importa mais do que a escolha do framework em si. Pinia foi escolhido por ser o gerenciador de estado padrão recomendado para Vue 3, com suporte nativo a TypeScript e API mais simples que alternativas como Vuex.

## 4. Estrutura do repositório: monorepo

**Alternativas consideradas**: repositórios separados para frontend e backend.

**Decisão**: monorepo único, com pastas `/frontend` e `/backend`, orquestrado por `docker-compose.yml` na raiz.

**Motivo**: facilita a avaliação (um único `git clone` e `docker-compose up` sobem o projeto inteiro), mantém o histórico de commits unificado mostrando a evolução de frontend e backend lado a lado, e simplifica a documentação. Deploy separado (Vercel para frontend, Railway para backend) continua possível a partir de subpastas do mesmo repositório, então não há perda de flexibilidade de deploy.

## 5. Catálogo de figurinhas: JSON estático no frontend

**Alternativas consideradas**:
- Criar endpoint de API e tabela no banco para servir o catálogo.
- Usar um bucket externo para armazenar o catálogo e/ou as imagens.
- Manter o catálogo e as imagens como arquivos estáticos do frontend.

**Decisão**: o catálogo de figurinhas é um JSON estático em `/frontend/src/data/figurinhas.json`, importado diretamente pelo frontend. As imagens correspondentes ficam em `/frontend/public/cards`. Não existe endpoint de API nem tabela no banco para figurinhas.

**Motivo**: o catálogo é fixo e pequeno, sem necessidade de CRUD, painel administrativo ou atualização dinâmica em produção. Modelar isso no banco e expor via API adicionaria complexidade sem benefício prático para o escopo atual. Manter o catálogo no frontend também elimina dependência externa de bucket, reduz pontos de falha e deixa as imagens versionadas junto com a vitrine. Essa abordagem é consistente com o restante do conteúdo estático da landing page: os dados usados apenas para apresentação vivem no frontend, enquanto o backend fica focado em leads, autenticação e kanban.

## 6. Distribuição round robin: persistência e concorrência

**Decisão**: o índice do próximo vendedor na fila round robin é persistido no banco de dados (não mantido em memória), garantindo que a distribuição sobreviva a reinícios do servidor e funcione corretamente em ambientes com múltiplas instâncias. A implementação usa uma tabela `round_robin_state` com um registro singleton (`id = 1`) e o campo `next_seller_order`, que aponta para a próxima posição da fila.

**Motivo**: manter o estado do round robin apenas em memória faria a distribuição "resetar" a cada deploy ou reinício, e quebraria em cenários com mais de uma instância do backend rodando simultaneamente (cada instância teria seu próprio contador). Persistir em banco resolve ambos os problemas.

**Concorrência**: cada criação de lead roda dentro de uma transação e bloqueia o registro singleton de `round_robin_state` com `SELECT ... FOR UPDATE` no PostgreSQL. Enquanto uma requisição calcula o vendedor, cria o lead e avança `next_seller_order`, as demais requisições concorrentes aguardam o commit dessa transação. Isso serializa apenas o trecho crítico do round robin e evita que duas requisições leiam o mesmo índice ao mesmo tempo. Nos testes locais com SQLite, que ignora `FOR UPDATE`, a transação usa `BEGIN IMMEDIATE` para obter um lock de escrita equivalente para validar o comportamento concorrente sem depender do PostgreSQL rodando localmente.

## 7. Documentação em português (pt-BR)

**Decisão**: toda documentação do projeto (README, este registro, documentação de arquitetura, AGENTS.md) é escrita em português. Código (nomes de variáveis, funções, classes, commits) permanece em inglês.

**Motivo**: alinhamento com o idioma do processo seletivo e do avaliador. Manter o código em inglês segue a convenção internacional mais comum, evitando mistura de idiomas dentro da própria base de código.
