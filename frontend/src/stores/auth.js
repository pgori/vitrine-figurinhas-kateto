import { defineStore } from "pinia";

import {
  clearStoredAuthToken,
  getStoredAuthToken,
  login,
  setStoredAuthToken,
} from "@/services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: getStoredAuthToken(),
    isLoading: false,
    errorMessage: "",
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    async login(credentials) {
      this.isLoading = true;
      this.errorMessage = "";

      try {
        const response = await login(credentials);
        this.token = response.access_token;
        setStoredAuthToken(response.access_token);
        return response;
      } catch {
        this.errorMessage = "Usuário ou senha inválidos.";
        throw new Error(this.errorMessage);
      } finally {
        this.isLoading = false;
      }
    },
    logout() {
      this.token = null;
      this.errorMessage = "";
      clearStoredAuthToken();
    },
  },
});
