import { useState } from "react";
import { VEHICLE_STATUSES, VEHICLE_TYPES, humanize } from "../lib/service.js";

const EMPTY = {
  name: "",
  plate: "",
  vehicle_type: "VAN",
  status: "ACTIVE",
  odometer_km: 0,
  service_interval_km: 10000,
  last_service_km: 0,
};

export default function VehicleModal({ vehicle, onClose, onSave }) {
  const [form, setForm] = useState(vehicle ? { ...EMPTY, ...pick(vehicle) } : EMPTY);
  const [saving, setSaving] = useState(false);
  const editing = Boolean(vehicle);

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    const payload = {
      ...form,
      odometer_km: Number(form.odometer_km),
      service_interval_km: Number(form.service_interval_km),
      last_service_km: Number(form.last_service_km),
    };
    await onSave(payload, vehicle);
    setSaving(false);
  }

  return (
    <div className="overlay" onClick={onClose} role="presentation">
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={submit} aria-label="Vehicle form">
        <h2>{editing ? `Edit ${vehicle.name}` : "Register a vehicle"}</h2>

        <div className="form-grid">
          <label>
            Name
            <input className="input" required maxLength={100} value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Van 12" />
          </label>
          <label>
            Plate
            <input className="input" required minLength={2} maxLength={20} value={form.plate} onChange={(e) => set("plate", e.target.value)} placeholder="MH 12 AB 1234" />
          </label>
          <label>
            Type
            <select className="input" value={form.vehicle_type} onChange={(e) => set("vehicle_type", e.target.value)}>
              {VEHICLE_TYPES.map((t) => (
                <option key={t} value={t}>{humanize(t)}</option>
              ))}
            </select>
          </label>
          <label>
            Status
            <select className="input" value={form.status} onChange={(e) => set("status", e.target.value)}>
              {VEHICLE_STATUSES.map((s) => (
                <option key={s} value={s}>{humanize(s)}</option>
              ))}
            </select>
          </label>
          <label>
            Odometer (km)
            <input className="input" type="number" min={0} value={form.odometer_km} onChange={(e) => set("odometer_km", e.target.value)} />
          </label>
          <label>
            Service interval (km)
            <input className="input" type="number" min={1} max={200000} value={form.service_interval_km} onChange={(e) => set("service_interval_km", e.target.value)} />
          </label>
          <label>
            Last service at (km)
            <input className="input" type="number" min={0} value={form.last_service_km} onChange={(e) => set("last_service_km", e.target.value)} />
          </label>
        </div>

        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Saving…" : editing ? "Save changes" : "Register"}
          </button>
        </div>
      </form>
    </div>
  );
}

function pick(v) {
  const { name, plate, vehicle_type, status, odometer_km, service_interval_km, last_service_km } = v;
  return { name, plate, vehicle_type, status, odometer_km, service_interval_km, last_service_km };
}
