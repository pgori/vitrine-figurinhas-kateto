<script setup>
import Draggable from "vuedraggable";

import KanbanCard from "@/components/KanbanCard.vue";

const props = defineProps({
  column: {
    type: String,
    required: true,
  },
  leads: {
    type: Array,
    required: true,
  },
  isDragging: {
    type: Boolean,
    default: false,
  },
  isHighlighted: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "card-dropped",
  "column-hover",
  "column-leave",
  "drag-end",
  "drag-start",
]);

function handleChange(event) {
  if (!event.added) {
    return;
  }

  emit("card-dropped", {
    lead: event.added.element,
    targetColumn: props.column,
  });
}
</script>

<template>
  <section
    class="kanban-column"
    :class="{
      'kanban-column--dragging': isDragging,
      'kanban-column--highlighted': isHighlighted,
    }"
    @dragenter="emit('column-hover')"
    @dragover.prevent="emit('column-hover')"
    @dragleave="emit('column-leave')"
  >
    <header class="kanban-column__header">
      <h2>{{ column }}</h2>
      <span>{{ leads.length }}</span>
    </header>

    <Draggable
      :list="leads"
      class="kanban-column__list"
      group="kanban-leads"
      item-key="id"
      ghost-class="kanban-card--ghost"
      chosen-class="kanban-card--chosen"
      drag-class="kanban-card--drag"
      :animation="180"
      @start="emit('drag-start')"
      @end="emit('drag-end')"
      @change="handleChange"
    >
      <template #item="{ element }">
        <KanbanCard :lead="element" />
      </template>

      <template #footer>
        <p v-if="leads.length === 0" class="kanban-column__empty">
          Nenhum card nesta coluna.
        </p>
      </template>
    </Draggable>
  </section>
</template>
