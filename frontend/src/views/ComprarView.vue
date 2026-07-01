<script setup>
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import FormularioCompra from "@/components/FormularioCompra.vue";
import figurinhas from "@/data/figurinhas.json";
import { useLeadsStore } from "@/stores/leads";

const route = useRoute();
const router = useRouter();
const leadsStore = useLeadsStore();

const selectedFigurinha = computed(() =>
  figurinhas.find((figurinha) => figurinha.id === route.query.item) ?? null,
);

watch(
  selectedFigurinha,
  (figurinha) => {
    leadsStore.setSelectedFigurinha(figurinha);
  },
  { immediate: true },
);

function goHome() {
  router.push("/");
}
</script>

<template>
  <main class="purchase-page" @click="goHome">
    <section class="purchase-layout" aria-labelledby="purchase-title" @click.stop>
      <aside class="selected-figurinha">
        <a class="back-link" href="/" @click.prevent="goHome">
          Voltar para a coleção
        </a>

        <template v-if="selectedFigurinha">
          <img
            :src="selectedFigurinha.imagem"
            :alt="`Figurinha ${selectedFigurinha.nome}`"
          />
          <span class="eyebrow">Figurinha selecionada</span>
          <h1 id="purchase-title">{{ selectedFigurinha.nome }}</h1>
          <p>{{ selectedFigurinha.descricao }}</p>
        </template>

        <template v-else>
          <span class="eyebrow">Pedido personalizado</span>
          <h1 id="purchase-title">Conte qual carta você procura</h1>
          <p>
            Nenhuma figurinha foi selecionada na vitrine. Você ainda pode
            escrever o nome da carta desejada no formulário.
          </p>
        </template>
      </aside>

      <section class="form-panel" aria-label="Formulário de compra">
        <FormularioCompra />
      </section>
    </section>
  </main>
</template>
