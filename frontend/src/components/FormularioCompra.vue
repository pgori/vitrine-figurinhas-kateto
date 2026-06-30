<script setup>
import { computed, reactive } from "vue";

import { useLeadsStore } from "@/stores/leads";

const leadsStore = useLeadsStore();

const errors = reactive({
  name: "",
  desiredItem: "",
  phone: "",
});

const form = computed(() => leadsStore.form);

function updateTextField(field, event) {
  leadsStore.updateField(field, event.target.value);
  errors[field] = "";
}

function updatePhone(event) {
  const onlyDigits = event.target.value.replace(/\D/g, "").slice(0, 11);
  leadsStore.updateField("phone", onlyDigits);
  errors.phone = "";
}

async function submitForm() {
  if (!validateForm()) {
    return;
  }

  try {
    await leadsStore.submitLead();
  } catch {
    // A store centraliza a mensagem exibida na interface.
  }
}

function validateForm() {
  errors.name = form.value.name.trim() ? "" : "Informe seu nome.";
  errors.desiredItem = form.value.desiredItem.trim()
    ? ""
    : "Informe a figurinha desejada.";
  errors.phone = /^\d{10,11}$/.test(form.value.phone)
    ? ""
    : "Informe um WhatsApp brasileiro com 10 ou 11 números.";

  return !errors.name && !errors.desiredItem && !errors.phone;
}
</script>

<template>
  <form class="purchase-form" novalidate @submit.prevent="submitForm">
    <label class="field">
      <span>Nome</span>
      <input
        :value="form.name"
        type="text"
        autocomplete="name"
        placeholder="Seu nome"
        @input="updateTextField('name', $event)"
      />
      <small v-if="errors.name">{{ errors.name }}</small>
    </label>

    <label class="field">
      <span>Figurinha desejada</span>
      <input
        :value="form.desiredItem"
        type="text"
        placeholder="Nome da carta"
        @input="updateTextField('desiredItem', $event)"
      />
      <small v-if="errors.desiredItem">{{ errors.desiredItem }}</small>
    </label>

    <label class="field">
      <span>Telefone com WhatsApp</span>
      <input
        :value="form.phone"
        type="tel"
        inputmode="numeric"
        autocomplete="tel"
        maxlength="11"
        placeholder="11999990000"
        @input="updatePhone"
      />
      <small v-if="errors.phone">{{ errors.phone }}</small>
    </label>

    <button
      class="button button--primary purchase-form__submit"
      type="submit"
      :disabled="leadsStore.isSubmitting"
    >
      {{ leadsStore.isSubmitting ? "Enviando..." : "Enviar pedido" }}
    </button>

    <p v-if="leadsStore.successMessage" class="form-message form-message--success">
      {{ leadsStore.successMessage }}
    </p>
    <p v-if="leadsStore.errorMessage" class="form-message form-message--error">
      {{ leadsStore.errorMessage }}
    </p>
  </form>
</template>
