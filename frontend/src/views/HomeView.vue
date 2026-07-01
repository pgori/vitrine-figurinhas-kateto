<script setup>
import { nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";

import FigurinhaCard from "@/components/FigurinhaCard.vue";
import figurinhas from "@/data/figurinhas.json";
import { useLeadsStore } from "@/stores/leads";

const router = useRouter();
const leadsStore = useLeadsStore();

function scrollToCollection() {
  document
    .querySelector("#colecao")
    ?.scrollIntoView({ behavior: "smooth" });
}

function goToPurchase(figurinha) {
  leadsStore.saveScrollPosition(window.scrollY);
  router.push({
    name: "comprar",
    query: { item: figurinha.id },
  });
}

onMounted(async () => {
  const scrollPosition = leadsStore.scrollPosition;

  if (scrollPosition <= 0) {
    return;
  }

  await nextTick();

  setTimeout(() => {
    window.scrollTo({ top: scrollPosition, behavior: "instant" });
    leadsStore.resetScrollPosition();
  }, 50);
});
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
        <button class="button button--primary" type="button" @click="scrollToCollection">
          Ver coleção
        </button>
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
          @purchase="goToPurchase"
        />
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="site-footer__brand">
      <p>Vitrine de Figurinhas Kateto</p>
      <span>Gwent, ouro e bons pactos comerciais.</span>
    </div>
    <p class="site-footer__legal">
      Este é um projeto fictício criado para fins educacionais. As imagens das
      cartas são propriedade da CD Projekt Red e foram obtidas em gwent.one.
      Gwent: The Witcher Card Game é marca registrada da CD Projekt Red. Este
      projeto não possui fins comerciais ou lucrativos.
    </p>
  </footer>
</template>
