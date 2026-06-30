<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import KanbanColuna from "@/components/KanbanColuna.vue";
import { useAuthStore } from "@/stores/auth";
import { KANBAN_COLUMNS, useKanbanStore } from "@/stores/kanban";

const authStore = useAuthStore();
const kanbanStore = useKanbanStore();
const router = useRouter();
const highlightedColumn = ref("");
const isDragging = ref(false);

onMounted(() => {
  kanbanStore.fetchKanban().catch(() => {});
});

function logout() {
  authStore.logout();
  router.push("/login");
}

function handleDragStart() {
  isDragging.value = true;
  kanbanStore.captureDragSnapshot();
}

function handleDragEnd() {
  isDragging.value = false;
  highlightedColumn.value = "";
}

async function handleCardDropped({ lead, targetColumn }) {
  try {
    await kanbanStore.moveLead(lead, targetColumn);
  } catch {
    // A store reverte o estado otimista e mantém a mensagem para a tela.
  }
}
</script>

<template>
  <main class="kanban-page">
    <header class="kanban-header">
      <div>
        <span class="eyebrow">CRM Kateto</span>
        <h1>Kanban de Leads</h1>
      </div>

      <button class="button button--secondary kanban-header__logout" type="button" @click="logout">
        Sair
      </button>
    </header>

    <p v-if="kanbanStore.errorMessage" class="form-message form-message--error">
      {{ kanbanStore.errorMessage }}
    </p>

    <p v-if="kanbanStore.isLoading" class="kanban-loading">Carregando cards...</p>

    <section class="kanban-board" aria-label="Quadro kanban de leads">
      <KanbanColuna
        v-for="column in KANBAN_COLUMNS"
        :key="column"
        :column="column"
        :leads="kanbanStore.leadsByColumn[column]"
        :is-dragging="isDragging"
        :is-highlighted="highlightedColumn === column"
        @drag-start="handleDragStart"
        @drag-end="handleDragEnd"
        @column-hover="highlightedColumn = column"
        @column-leave="highlightedColumn = ''"
        @card-dropped="handleCardDropped"
      />
    </section>
  </main>
</template>
