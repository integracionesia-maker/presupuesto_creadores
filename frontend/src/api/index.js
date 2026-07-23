/**
 * Thin API wrapper around the FastAPI backend.
 * All calls return parsed JSON; errors throw with a descriptive message.
 * Cookies de sesión (access/refresh) viajan en cada request; un 401 dispara
 * un intento de refresh automático y reintenta la petición original una vez.
 */

const BASE = "/api";
const NO_RETRY_PATHS = ["/auth/login", "/auth/refresh"];

/**
 * Distingue una falla de RED (el fetch nunca obtuvo respuesta — servidor
 * caído, sin internet) de un error HTTP normal (el servidor respondió con
 * un status de error, manejado por `request()` arriba con `body.detail`).
 * El Fetch API siempre lanza `TypeError` para fallas de red en todos los
 * navegadores (Chrome: "Failed to fetch", Firefox: "NetworkError...",
 * Safari: "Load failed") — se complementa con un chequeo de mensaje por si
 * algún entorno lanza otro tipo de error para el mismo caso.
 */
export function isNetworkError(e) {
  if (!e) return false;
  if (e instanceof TypeError) return true;
  return /failed to fetch|network ?error|internet_disconnected|load failed/i.test(String(e.message || ""));
}

let onAuthFailure = null;
export function setAuthFailureHandler(handler) {
  onAuthFailure = handler;
}

let refreshPromise = null;
function refreshSession() {
  if (!refreshPromise) {
    refreshPromise = fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    }).finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

async function fetchWithAuthRetry(path, options = {}, skipAuthRetry = false) {
  const res = await fetch(`${BASE}${path}`, { credentials: "include", ...options });

  if (res.status === 401 && !skipAuthRetry && !NO_RETRY_PATHS.some((p) => path.startsWith(p))) {
    const refreshRes = await refreshSession();
    if (refreshRes.ok) {
      return fetchWithAuthRetry(path, options, true);
    }
    if (onAuthFailure) onAuthFailure();
  }

  return res;
}

async function request(path, options = {}) {
  const res = await fetchWithAuthRetry(path, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}: ${res.statusText}`);
  }

  return res.json();
}

/* ── Auth ────────────────────────────────────────────────────────────────── */

export function login(identificador, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ identificador, password }),
  });
}

export function logout() {
  return request("/auth/logout", { method: "POST" });
}

export function fetchMe() {
  return request("/auth/me");
}

export function updateMe(data) {
  return request("/auth/me", { method: "PUT", body: JSON.stringify(data) });
}

export function changePassword(currentPassword, newPassword) {
  return request("/auth/change-password", {
    method: "POST",
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
}

/* ── Usuarios (Administración) ──────────────────────────────────────────── */

export function fetchUsers(role) {
  const qs = role ? `?role=${role}` : "";
  return request(`/users/${qs}`);
}

export function createUser(data) {
  return request("/users/", { method: "POST", body: JSON.stringify(data) });
}

export function updateUser(id, data) {
  return request(`/users/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export function resetUserPassword(id) {
  return request(`/users/${id}/reset-password`, { method: "POST" });
}

export function setUserActive(id, isActive) {
  return request(`/users/${id}/estado`, {
    method: "PATCH",
    body: JSON.stringify({ is_active: isActive }),
  });
}

/* ── Creators ────────────────────────────────────────────────────────────── */

export function fetchCreators(activeOnly = false) {
  const qs = activeOnly ? "?active_only=true" : "";
  return request(`/creators/${qs}`);
}

export function fetchCreatorsKpi() {
  return request("/creators/kpi");
}

export function createCreator(data) {
  return request("/creators/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateCreator(id, data) {
  return request(`/creators/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function fetchCreatorCycles(id) {
  return request(`/creators/${id}/ciclos`);
}

/* ── Brands ──────────────────────────────────────────────────────────────── */

export function fetchBrands(activeOnly = true) {
  const qs = activeOnly ? "?active_only=true" : "";
  return request(`/brands/${qs}`);
}

export function createBrand(data) {
  return request("/brands/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateBrand(id, data) {
  return request(`/brands/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/* ── Tickets ─────────────────────────────────────────────────────────────── */

export function fetchTickets({ creatorName, brandName, status } = {}) {
  const params = new URLSearchParams();
  if (creatorName) params.set("creator_name", creatorName);
  if (brandName) params.set("brand_name", brandName);
  if (status) params.set("status", status);
  const qs = params.toString();
  return request(`/tickets/${qs ? `?${qs}` : ""}`);
}

export function approveTicket(id) {
  return request(`/tickets/${id}/aprobar`, { method: "POST" });
}

export function rejectTicket(id, reason) {
  return request(`/tickets/${id}/rechazar`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function fetchBrandSpendBreakdown(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const qs = params.toString();
  return request(`/tickets/brand-spend${qs ? `?${qs}` : ""}`);
}

export async function uploadTicket({ creatorId, brandId, amount, notes, file }) {
  const formData = new FormData();
  formData.append("creator_id", creatorId);
  formData.append("brand_id", brandId);
  formData.append("amount", amount);
  if (notes) formData.append("notes", notes);
  formData.append("file", file);

  const res = await fetchWithAuthRetry("/tickets/", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}`);
  }

  return res.json();
}

export function ticketFileUrl(ticketId) {
  return `${BASE}/tickets/file/${ticketId}`;
}

export function softDeleteTicket(id) {
  return request(`/tickets/${id}/soft-delete`, { method: "POST" });
}

export function hardDeleteTicket(id) {
  return request(`/tickets/${id}/permanent`, { method: "DELETE" });
}

/* ── Gastos Generales ────────────────────────────────────────────────────── */

export function fetchGeneralExpenses({ startDate, endDate } = {}) {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const qs = params.toString();
  return request(`/general-expenses/${qs ? `?${qs}` : ""}`);
}

export async function createGeneralExpense({ brandId, amount, description, file }) {
  const formData = new FormData();
  formData.append("brand_id", brandId);
  formData.append("amount", amount);
  formData.append("description", description);
  formData.append("file", file);

  const res = await fetchWithAuthRetry("/general-expenses/", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}`);
  }

  return res.json();
}

export function softDeleteGeneralExpense(id) {
  return request(`/general-expenses/${id}/soft-delete`, { method: "POST" });
}

export function hardDeleteGeneralExpense(id) {
  return request(`/general-expenses/${id}/permanent`, { method: "DELETE" });
}

export function generalExpenseFileUrl(id) {
  return `${BASE}/general-expenses/${id}/file`;
}

export function fetchGeneralExpensesExport(months) {
  const params = new URLSearchParams();
  params.set("months", months.join(","));
  return request(`/general-expenses/export?${params.toString()}`);
}

/* ── Dashboard ─────────────────────────────────────────────────────────────── */

export function fetchDashboardSummary(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const qs = params.toString();
  return request(`/dashboard/summary${qs ? `?${qs}` : ""}`);
}

export function fetchMonthlySpend(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const qs = params.toString();
  return request(`/dashboard/monthly-spend${qs ? `?${qs}` : ""}`);
}

export function fetchCreatorUsage(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const qs = params.toString();
  return request(`/dashboard/creator-usage${qs ? `?${qs}` : ""}`);
}

export function fetchGeneralExpensesMonthly(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.set("start_date", startDate);
  if (endDate) params.set("end_date", endDate);
  const qs = params.toString();
  return request(`/dashboard/general-expenses-monthly${qs ? `?${qs}` : ""}`);
}
