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

## 5. Armazenamento de imagens: Cloudflare R2 + fallback estático

**Alternativas consideradas**:
- Apontar diretamente para URLs de imagens do site gwent.one (hotlinking).
- Servir todas as imagens como assets estáticos do frontend.

**Decisão**: Cloudflare R2 como fonte principal das imagens das figurinhas, com um pequeno subconjunto de imagens também presente em `/frontend/public/cards` como fallback.

**Motivo**: hotlinking para gwent.one foi descartado por risco de quebra em produção (bloqueio por referer/CORS, mudança de URL, indisponibilidade fora do nosso controle) e por não demonstrar autonomia sobre a própria infraestrutura. Servir todas as imagens como assets estáticos aumentaria o tamanho do repositório desnecessariamente. R2 foi escolhido por não cobrar taxas de egress (diferente de S3) e por ser compatível com a API S3, mantendo a integração simples. O fallback estático local existe como rede de segurança caso o bucket fique temporariamente indisponível, sem precisar duplicar todo o catálogo de imagens.

## 6. Distribuição round robin: persistência e concorrência

**Decisão**: o índice do próximo vendedor na fila round robin é persistido no banco de dados (não mantido em memória), garantindo que a distribuição sobreviva a reinícios do servidor e funcione corretamente em ambientes com múltiplas instâncias.

**Motivo**: manter o estado do round robin apenas em memória faria a distribuição "resetar" a cada deploy ou reinício, e quebraria em cenários com mais de uma instância do backend rodando simultaneamente (cada instância teria seu próprio contador). Persistir em banco resolve ambos os problemas. Para evitar condições de corrida em caso de requisições simultâneas, [a definir na implementação: usar transação com lock a nível de linha / constraint de unicidade — detalhar aqui assim que implementado].

## 7. Documentação em português (pt-BR)

**Decisão**: toda documentação do projeto (README, este registro, documentação de arquitetura, AGENTS.md) é escrita em português. Código (nomes de variáveis, funções, classes, commits) permanece em inglês.

**Motivo**: alinhamento com o idioma do processo seletivo e do avaliador. Manter o código em inglês segue a convenção internacional mais comum, evitando mistura de idiomas dentro da própria base de código.