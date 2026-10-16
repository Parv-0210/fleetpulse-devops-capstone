const BASE = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (response.status === 204) return null;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(body.detail)
      ? body.detail.map((d) => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join("; ")
      : body.detail || `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return body;
}

export const api = {
  stats: () => request("/fleet/stats"),
  listVehicles: (params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString();
    return request(`/vehicles${qs ? `?${qs}` : ""}`);
  },
  createVehicle: (data) => request("/vehicles", { method: "POST", body: JSON.stringify(data) }),
  updateVehicle: (id, data) => request(`/vehicles/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteVehicle: (id) => request(`/vehicles/${id}`, { method: "DELETE" }),
  listServices: (id) => request(`/vehicles/${id}/services`),
  logService: (id, data) => request(`/vehicles/${id}/services`, { method: "POST", body: JSON.stringify(data) }),
  deleteService: (recordId) => request(`/services/${recordId}`, { method: "DELETE" }),
};
