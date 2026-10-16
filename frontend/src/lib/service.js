/**
 * Pure helpers shared by the UI. Kept framework-free so they can be unit tested
 * with Node's built-in test runner (no extra tooling in the image).
 */

export const SERVICE_STATE = {
  OK: { label: "Healthy", tone: "ok" },
  DUE_SOON: { label: "Due soon", tone: "warn" },
  OVERDUE: { label: "Overdue", tone: "danger" },
};

export const VEHICLE_TYPES = ["VAN", "TRUCK", "CAR", "BIKE"];
export const VEHICLE_STATUSES = ["ACTIVE", "IN_SHOP", "RETIRED"];
export const SERVICE_TYPES = ["OIL_CHANGE", "TIRES", "BRAKES", "INSPECTION", "REPAIR", "OTHER"];

export function formatKm(value) {
  const n = Number(value) || 0;
  return `${n.toLocaleString("en-IN")} km`;
}

export function formatMoney(value) {
  const n = Number(value) || 0;
  return n.toLocaleString("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
}

export function humanize(token) {
  return String(token || "")
    .toLowerCase()
    .split("_")
    .map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w))
    .join(" ");
}

export function stateMeta(state) {
  return SERVICE_STATE[state] || { label: humanize(state), tone: "neutral" };
}

/** Percentage of the service interval already consumed, clamped to 0-100. */
export function intervalUsedPct(vehicle) {
  const interval = Number(vehicle.service_interval_km) || 1;
  const used = Number(vehicle.odometer_km) - Number(vehicle.last_service_km);
  return Math.max(0, Math.min(100, Math.round((used / interval) * 100)));
}

/** Sort: overdue first, then due soon, then healthy; ties by least km remaining. */
export function sortByUrgency(vehicles) {
  const rank = { OVERDUE: 0, DUE_SOON: 1, OK: 2 };
  return [...vehicles].sort((a, b) => {
    const r = (rank[a.service_state] ?? 9) - (rank[b.service_state] ?? 9);
    return r !== 0 ? r : a.km_until_service - b.km_until_service;
  });
}

export function relativeDate(iso) {
  if (!iso) return "never";
  const diffDays = Math.round((Date.now() - new Date(iso).getTime()) / 86_400_000);
  if (diffDays <= 0) return "today";
  if (diffDays === 1) return "yesterday";
  if (diffDays < 30) return `${diffDays} days ago`;
  const months = Math.round(diffDays / 30);
  return months === 1 ? "a month ago" : `${months} months ago`;
}
