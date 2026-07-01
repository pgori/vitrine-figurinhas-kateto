<script setup>
import { computed, reactive, ref } from "vue";

import { useLeadsStore } from "@/stores/leads";

const leadsStore = useLeadsStore();

const errors = reactive({
  name: "",
  desiredItem: "",
  phone: "",
});

const form = computed(() => leadsStore.form);
const phoneWasBlurred = ref(false);
const phoneDigits = computed(() => getPhoneDigits(form.value.phone));
const formattedPhone = computed(() => formatPhone(form.value.phone));
const hasDesiredItem = computed(() => form.value.desiredItem.trim().length > 0);
const isNameValid = computed(() => form.value.name.trim().length >= 3);
const isPhoneValid = computed(() => {
  return phoneDigits.value.length === 10 || phoneDigits.value.length === 11;
});
const canSubmit = computed(() => {
  return (
    hasDesiredItem.value &&
    isNameValid.value &&
    isPhoneValid.value &&
    !leadsStore.isSubmitting
  );
});

function getPhoneDigits(value) {
  return value.replace(/\D/g, "").slice(0, 11);
}

function formatPhone(value) {
  const digits = getPhoneDigits(value);

  if (digits.length <= 2) {
    return digits ? `(${digits}` : "";
  }

  if (digits.length <= 6) {
    return `(${digits.slice(0, 2)})${digits.slice(2)}`;
  }

  if (digits.length <= 10) {
    return `(${digits.slice(0, 2)})${digits.slice(2, 6)}-${digits.slice(6)}`;
  }

  return `(${digits.slice(0, 2)})${digits.slice(2, 7)}-${digits.slice(7)}`;
}

function updateTextField(field, event) {
  leadsStore.updateField(field, event.target.value);
  errors[field] = "";
}

function updatePhone(event) {
  const onlyDigits = getPhoneDigits(event.target.value);
  leadsStore.updateField("phone", onlyDigits);
  errors.phone =
    phoneWasBlurred.value && !isPhoneValid.value
      ? "Informe um WhatsApp brasileiro com 10 ou 11 números."
      : "";
}

function validatePhoneOnBlur() {
  phoneWasBlurred.value = true;
  errors.phone = isPhoneValid.value
    ? ""
    : "Informe um WhatsApp brasileiro com 10 ou 11 números.";
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
  errors.name = isNameValid.value
    ? ""
    : "Informe seu nome com ao menos 3 caracteres.";
  errors.desiredItem = form.value.desiredItem.trim()
    ? ""
    : "Informe a figurinha desejada.";
  errors.phone = isPhoneValid.value
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
        readonly
        placeholder="Nome da carta"
      />
      <small v-if="errors.desiredItem">{{ errors.desiredItem }}</small>
    </label>

    <label class="field">
      <span>Telefone com WhatsApp</span>
      <input
        :value="formattedPhone"
        type="tel"
        inputmode="numeric"
        autocomplete="tel"
        maxlength="14"
        placeholder="(11)99999-0000"
        @input="updatePhone"
        @blur="validatePhoneOnBlur"
      />
      <small v-if="errors.phone">{{ errors.phone }}</small>
    </label>

    <button
      class="button button--primary purchase-form__submit"
      type="submit"
      :disabled="!canSubmit"
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
