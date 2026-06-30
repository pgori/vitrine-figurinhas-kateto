<script setup>
import { computed } from "vue";

const props = defineProps({
  lead: {
    type: Object,
    required: true,
  },
});

const createdAt = computed(() =>
  new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(props.lead.created_at)),
);
</script>

<template>
  <article class="kanban-card">
    <h3>{{ lead.name }}</h3>
    <dl>
      <div>
        <dt>Figurinha</dt>
        <dd>{{ lead.desired_item }}</dd>
      </div>
      <div>
        <dt>WhatsApp</dt>
        <dd>{{ lead.phone }}</dd>
      </div>
      <div>
        <dt>Vendedor</dt>
        <dd>{{ lead.assigned_seller?.name ?? "Sem vendedor" }}</dd>
      </div>
      <div>
        <dt>Criado em</dt>
        <dd>{{ createdAt }}</dd>
      </div>
    </dl>
  </article>
</template>
