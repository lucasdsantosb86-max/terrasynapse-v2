// src/services/api.ts
export const API_URL =
  process.env.REACT_APP_API_URL ?? "http://localhost:8000";

function getToken() {
  return localStorage.getItem("ts_jwt");
}

async function http<T = any>(path: string, init: RequestInit = {}, auth = false): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };
  if (auth) {
    const t = getToken();
    if (t) headers["Authorization"] = `Bearer ${t}`;
  }
  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = await res.text(); } catch {}
    throw new Error(msg || "Erro na requisição");
  }
  return res.json();
}

export async function login(email: string, password: string) {
  // Ajuste para o seu backend se ele usar "username"
  return http<{ access_token: string; token_type: string }>(
    "/login",
    { method: "POST", body: JSON.stringify({ email, password }) }
  );
}

export async function register(payload: { name?: string; email: string; password: string }) {
  return http("/register", { method: "POST", body: JSON.stringify(payload) });
}

export async function getDashboard(lat: number, lon: number) {
  return http(`/dashboard/${lat}/${lon}`, { method: "GET" }, true);
}

export function saveToken(token: string) { localStorage.setItem("ts_jwt", token); }
export function logout()             { localStorage.removeItem("ts_jwt"); }
