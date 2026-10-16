import { useEffect, useState } from "react";
import { api } from "../api.js";
import { SERVICE_TYPES, formatKm, formatMoney, humanize } from "../lib/service.js";

export default function ServiceDrawer({ vehicle, onClose, onChanged, notify }) {
  const [records, setRecords] = useState(null);
  const [form, setForm] = useState({ service_type: "OIL_CHANGE", odometer_km: vehicle.odometer_km, cost: "", notes: "" });
  const [saving, setSaving] = useState(false);

  async function refresh() {
    try {
      setRecords(await api.listServices(vehicle.id));
    } catch (err) {
      notify(err.message, "danger");
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicle.id]);

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.logService(vehicle.id, {
        service_type: form.service_type,
        odometer_km: Number(form.odometer_km),
        cost: Number(form.cost) || 0,
        notes: form.notes,
      });
      notify(`${humanize(form.service_type)} logged for ${vehicle.name}`);
      setForm((f) => ({ ...f, cost: "", notes: "" }));
      await Promise.all([refresh(), onChanged()]);
    } catch (err) {
      notify(err.message, "danger");
    } finally {
      setSaving(false);
    }
  }

  async function remove(record) {
    try {
      await api.deleteService(record.id);
      await Promise.all([refresh(), onChanged()]);
    } catch (err) {
      notify(err.message, "danger");
    }
  }

  return (
    <div className="overlay" onClick={onClose} role="presentation">
      <aside className="drawer" onClick={(e) => e.stopPropagation()} aria-label="Service history">
        <header className="drawer-head">
          <div>
            <p className="eyebrow">Service log</p>
            <h2>{vehicle.name} <code className="plate">{vehicle.plate}</code></h2>
          </div>
          <button className="btn btn-ghost" onClick={onClose} aria-label="Close">✕</button>
        </header>

        <form className="service-form" onSubmit={submit}>
          <select className="input" value={form.service_type} onChange={(e) => setForm({ ...form, service_type: e.target.value })}>
            {SERVICE_TYPES.map((t) => (
              <option key={t} value={t}>{humanize(t)}</option>
            ))}
          </select>
          <input className="input" type="number" min={0} required value={form.odometer_km} onChange={(e) => setForm({ ...form, odometer_km: e.target.value })} placeholder="Odometer km" />
          <input className="input" type="number" min={0} step="0.01" value={form.cost} onChange={(e) => setForm({ ...form, cost: e.target.value })} placeholder="Cost (₹)" />
          <input className="input notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Notes (optional)" maxLength={2000} />
          <button className="btn btn-primary" type="submit" disabled={saving}>{saving ? "Logging…" : "Log service"}</button>
        </form>

        {records === null ? (
          <p className="muted">Loading history…</p>
        ) : records.length === 0 ? (
          <p className="muted">No services logged yet. The first entry resets the maintenance counter.</p>
        ) : (
          <ul className="timeline">
            {records.map((r) => (
              <li key={r.id}>
                <div className="timeline-row">
                  <strong>{humanize(r.service_type)}</strong>
                  <span className="muted">{new Date(r.performed_at).toLocaleDateString()}</span>
                </div>
                <div className="timeline-row">
                  <span>{formatKm(r.odometer_km)} · {formatMoney(r.cost)}</span>
                  <button className="btn btn-ghost btn-danger" onClick={() => remove(r)}>Delete</button>
                </div>
                {r.notes && <p className="muted">{r.notes}</p>}
              </li>
            ))}
          </ul>
        )}
      </aside>
    </div>
  );
}
