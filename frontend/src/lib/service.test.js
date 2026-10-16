import { test } from "node:test";
import assert from "node:assert/strict";
import { formatKm, humanize, intervalUsedPct, sortByUrgency, stateMeta } from "./service.js";

test("humanize turns API tokens into labels", () => {
  assert.equal(humanize("OIL_CHANGE"), "Oil Change");
  assert.equal(humanize("IN_SHOP"), "In Shop");
});

test("formatKm adds thousands separators and a unit", () => {
  assert.equal(formatKm(24000), "24,000 km");
  assert.equal(formatKm(undefined), "0 km");
});

test("intervalUsedPct is clamped between 0 and 100", () => {
  assert.equal(intervalUsedPct({ odometer_km: 25000, last_service_km: 20000, service_interval_km: 10000 }), 50);
  assert.equal(intervalUsedPct({ odometer_km: 99000, last_service_km: 20000, service_interval_km: 10000 }), 100);
  assert.equal(intervalUsedPct({ odometer_km: 100, last_service_km: 500, service_interval_km: 10000 }), 0);
});

test("sortByUrgency puts overdue vehicles first", () => {
  const sorted = sortByUrgency([
    { id: 1, service_state: "OK", km_until_service: 9000 },
    { id: 2, service_state: "OVERDUE", km_until_service: -300 },
    { id: 3, service_state: "DUE_SOON", km_until_service: 200 },
  ]);
  assert.deepEqual(sorted.map((v) => v.id), [2, 3, 1]);
});

test("stateMeta falls back gracefully for unknown states", () => {
  assert.equal(stateMeta("OVERDUE").tone, "danger");
  assert.equal(stateMeta("WEIRD").tone, "neutral");
});
