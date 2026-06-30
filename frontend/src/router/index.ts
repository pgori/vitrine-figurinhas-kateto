import { createRouter, createWebHistory } from "vue-router";

import ComprarView from "@/views/ComprarView.vue";
import HomeView from "@/views/HomeView.vue";
import KanbanView from "@/views/KanbanView.vue";
import LoginView from "@/views/LoginView.vue";
import { useAuthStore } from "@/stores/auth";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/comprar",
    name: "comprar",
    component: ComprarView,
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: "/kanban",
    name: "kanban",
    component: KanbanView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: "login",
      query: { redirect: to.fullPath },
    };
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { name: "kanban" };
  }

  return true;
});

export default router;
