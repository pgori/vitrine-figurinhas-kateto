const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const AUTH_TOKEN_STORAGE_KEY = "vitrine_figurinhas_auth_token";


export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}


export function getStoredAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
}


export function setStoredAuthToken(token) {
  localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
}


export function clearStoredAuthToken() {
  localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
}


export async function login(credentials) {
  return apiFetch("/login", {
    method: "POST",
    body: {
      username: credentials.username,
      password: credentials.password,
    },
  });
}


export async function createLead(payload) {
  return apiFetch("/leads", {
    method: "POST",
    body: {
      name: payload.name,
      desired_item: payload.desiredItem,
      phone: payload.phone,
    },
  });
}


export async function getLeadsByColumn(column) {
  const query = new URLSearchParams({ column });
  return apiFetch(`/leads?${query.toString()}`, {
    authenticated: true,
  });
}


export async function updateLeadColumn(leadId, column) {
  return apiFetch(`/leads/${leadId}`, {
    method: "PATCH",
    authenticated: true,
    body: {
      kanban_column: column,
    },
  });
}


async function apiFetch(path, options = {}) {
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers ?? {}),
  };

  if (options.authenticated) {
    const token = getStoredAuthToken();

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(extractApiError(data), response.status, data);
  }

  return data;
}


function extractApiError(data) {
  if (!data) {
    return "Não foi possível concluir a solicitação agora.";
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail) && data.detail.length > 0) {
    return data.detail[0]?.msg ?? "Dados inválidos.";
  }

  return "Não foi possível concluir a solicitação agora.";
}
