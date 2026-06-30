<script setup>
import FigurinhaCard from "@/components/FigurinhaCard.vue";
import figurinhas from "@/data/figurinhas.json";
</script>

<template>
  <main class="public-page">
    <section class="hero-section" aria-labelledby="hero-title">
      <div class="hero-section__copy">
        <span class="eyebrow">Cartas de Gwent para colecionadores</span>
        <h1 id="hero-title">Monte uma coleção digna das lendas do Continente</h1>
        <p>
          Figurinhas inspiradas nos grandes nomes de The Witcher 3, selecionadas
          para quem carrega o baralho como um troféu de guerra.
        </p>
        <a class="button button--primary" href="#colecao">Ver coleção</a>
      </div>

      <div class="hero-section__gallery" aria-hidden="true">
        <img
          v-for="figurinha in figurinhas.slice(0, 3)"
          :key="figurinha.id"
          :src="figurinha.imagem"
          :alt="figurinha.nome"
        />
      </div>
    </section>

    <section id="colecao" class="collection-section" aria-labelledby="collection-title">
      <div class="section-heading">
        <span class="eyebrow">Vitrine</span>
        <h2 id="collection-title">Escolha sua próxima figurinha</h2>
      </div>

      <div class="figurinha-grid">
        <FigurinhaCard
          v-for="figurinha in figurinhas"
          :key="figurinha.id"
          :figurinha="figurinha"
        />
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <p>Vitrine de Figurinhas Kateto</p>
    <span>Gwent, ouro e bons pactos comerciais.</span>
  </footer>
</template>
