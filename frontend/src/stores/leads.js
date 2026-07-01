import { defineStore } from "pinia";

import { createLead } from "@/services/api";

const initialForm = {
  name: "",
  desiredItem: "",
  phone: "",
};

export const useLeadsStore = defineStore("leads", {
  state: () => ({
    form: { ...initialForm },
    selectedFigurinha: null,
    isSubmitting: false,
    successMessage: "",
    errorMessage: "",
    createdLead: null,
    scrollPosition: 0,
  }),
  actions: {
    setSelectedFigurinha(figurinha) {
      this.selectedFigurinha = figurinha ?? null;

      if (figurinha) {
        this.form.desiredItem = figurinha.nome;
      } else {
        this.form.desiredItem = "";
      }
    },
    updateField(field, value) {
      this.form[field] = value;
      this.successMessage = "";
      this.errorMessage = "";
    },
    saveScrollPosition(position) {
      this.scrollPosition = position;
    },
    resetScrollPosition() {
      this.scrollPosition = 0;
    },
    async submitLead() {
      this.isSubmitting = true;
      this.successMessage = "";
      this.errorMessage = "";
      this.createdLead = null;

      try {
        const createdLead = await createLead(this.form);
        this.createdLead = createdLead;
        this.successMessage =
          "Solicitação enviada. Nosso time de vendas vai chamar você pelo WhatsApp.";
        this.form.name = "";
        this.form.phone = "";
        return createdLead;
      } catch (error) {
        this.errorMessage =
          error instanceof Error
            ? error.message
            : "Não foi possível enviar sua solicitação agora.";
        throw error;
      } finally {
        this.isSubmitting = false;
      }
    },
  },
});
