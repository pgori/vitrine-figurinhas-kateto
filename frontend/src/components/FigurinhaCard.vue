<script setup>
import { computed } from "vue";

const props = defineProps({
  figurinha: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["purchase"]);

const rarityClass = computed(() => `rarity-${props.figurinha.raridade}`);

const rarityLabel = computed(() => {
  const labels = {
    lendaria: "Lendária",
    epica: "Épica",
    rara: "Rara",
    comum: "Comum",
  };

  return labels[props.figurinha.raridade] ?? props.figurinha.raridade;
});

const formattedPrice = computed(() =>
  new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(props.figurinha.preco),
);

function goToPurchase() {
  emit("purchase", props.figurinha);
}
</script>

<template>
  <article class="figurinha-card">
    <div class="figurinha-card__image-frame">
      <img
        class="figurinha-card__image"
        :src="figurinha.imagem"
        :alt="`Figurinha ${figurinha.nome}`"
        loading="lazy"
      />
    </div>

    <div class="figurinha-card__content">
      <div class="figurinha-card__meta">
        <span class="rarity-badge" :class="rarityClass">{{ rarityLabel }}</span>
        <strong>{{ formattedPrice }}</strong>
      </div>

      <h3>{{ figurinha.nome }}</h3>
      <p>{{ figurinha.descricao }}</p>

      <button class="button button--secondary" type="button" @click="goToPurchase">
        Quero essa
      </button>
    </div>
  </article>
</template>
