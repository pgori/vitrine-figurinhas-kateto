import { defineStore } from "pinia";

import { getLeadsByColumn, updateLeadColumn } from "@/services/api";

export const KANBAN_COLUMNS = [
  "Sem Contato",
  "Em Contato",
  "Perdido",
  "Finalizado",
];

function createEmptyColumns() {
  return Object.fromEntries(KANBAN_COLUMNS.map((column) => [column, []]));
}

export const useKanbanStore = defineStore("kanban", {
  state: () => ({
    leadsByColumn: createEmptyColumns(),
    isLoading: false,
    errorMessage: "",
    dragSnapshot: null,
  }),
  getters: {
    totalLeads: (state) =>
      KANBAN_COLUMNS.reduce(
        (total, column) => total + state.leadsByColumn[column].length,
        0,
      ),
  },
  actions: {
    async fetchKanban() {
      this.isLoading = true;
      this.errorMessage = "";

      try {
        const entries = await Promise.all(
          KANBAN_COLUMNS.map(async (column) => [column, await getLeadsByColumn(column)]),
        );
        this.leadsByColumn = Object.fromEntries(entries);
      } catch (error) {
        this.errorMessage =
          error instanceof Error
            ? error.message
            : "Não foi possível carregar o kanban.";
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    captureDragSnapshot() {
      this.dragSnapshot = Object.fromEntries(
        KANBAN_COLUMNS.map((column) => [
          column,
          this.leadsByColumn[column].map((lead) => ({ ...lead })),
        ]),
      );
    },
    clearDragSnapshot() {
      this.dragSnapshot = null;
    },
    async moveLead(lead, targetColumn) {
      const sourceColumn = lead.kanban_column;

      if (sourceColumn === targetColumn) {
        this.clearDragSnapshot();
        return;
      }

      lead.kanban_column = targetColumn;

      try {
        const updatedLead = await updateLeadColumn(lead.id, targetColumn);
        const targetList = this.leadsByColumn[targetColumn];
        const targetIndex = targetList.findIndex((item) => item.id === lead.id);

        if (targetIndex !== -1) {
          targetList[targetIndex] = updatedLead;
        }

        this.clearDragSnapshot();
      } catch (error) {
        if (this.dragSnapshot) {
          this.leadsByColumn = this.dragSnapshot;
        }

        this.clearDragSnapshot();
        this.errorMessage =
          error instanceof Error
            ? error.message
            : "Não foi possível mover o card.";
        throw error;
      }
    },
  },
});
