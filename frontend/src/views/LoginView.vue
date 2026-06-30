<script setup>
import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

async function submitLogin() {
  try {
    await authStore.login(form);
    router.push(route.query.redirect?.toString() || "/kanban");
  } catch {
    // A store centraliza a mensagem de erro exibida na interface.
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel" aria-labelledby="login-title">
      <span class="eyebrow">Área do time de vendas</span>
      <h1 id="login-title">Entrar no CRM</h1>

      <form class="auth-form" @submit.prevent="submitLogin">
        <label class="field">
          <span>Usuário</span>
          <input
            v-model="form.username"
            type="text"
            autocomplete="username"
            placeholder="admin"
            required
          />
        </label>

        <label class="field">
          <span>Senha</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
          />
        </label>

        <button class="button button--primary" type="submit" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? "Entrando..." : "Entrar" }}
        </button>

        <p v-if="authStore.errorMessage" class="form-message form-message--error">
          {{ authStore.errorMessage }}
        </p>
      </form>
    </section>
  </main>
</template>
