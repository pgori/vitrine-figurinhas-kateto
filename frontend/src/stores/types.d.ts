declare module "@/stores/auth" {
  export function useAuthStore(): {
    token: string | null;
    isLoading: boolean;
    errorMessage: string;
    isAuthenticated: boolean;
    login(credentials: { username: string; password: string }): Promise<unknown>;
    logout(): void;
  };
}

declare module "@/stores/kanban" {
  export const KANBAN_COLUMNS: string[];

  export function useKanbanStore(): {
    leadsByColumn: Record<string, unknown[]>;
    isLoading: boolean;
    errorMessage: string;
    totalLeads: number;
    fetchKanban(): Promise<void>;
    captureDragSnapshot(): void;
    clearDragSnapshot(): void;
    moveLead(lead: Record<string, unknown>, targetColumn: string): Promise<void>;
  };
}
