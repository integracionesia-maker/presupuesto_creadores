/**
 * Thin API wrapper around the FastAPI backend.
 * All calls return parsed JSON; errors throw with a descriptive message.
 */

const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}: ${res.statusText}`);
  }

  return res.json();
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

export function fetchTickets({ creatorName, brandName } = {}) {
  const params = new URLSearchParams();
  if (creatorName) params.set("creator_name", creatorName);
  if (brandName) params.set("brand_name", brandName);
  const qs = params.toString();
  return request(`/tickets/${qs ? `?${qs}` : ""}`);
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

  const res = await fetch(`${BASE}/tickets/`, {
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
