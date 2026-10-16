import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api.js";
import { sortByUrgency } from "./lib/service.js";
import Sidebar from "./components/Sidebar.jsx";
import KpiGrid from "./components/KpiGrid.jsx";
import VehicleCard from "./components/VehicleCard.jsx";
import VehicleModal from "./components/VehicleModal.jsx";
import ServiceDrawer from "./components/ServiceDrawer.jsx";
import Toast from "./components/Toast.jsx";

const REFRESH_MS = 20_000;

export default function App() {
  const [vehicles, setVehicles] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [query, setQuery] = useState("");
  const [modal, setModal] = useState(null); // { mode: "create" } | { mode: "edit", vehicle }
  const [drawerVehicle, setDrawerVehicle] = useState(null);
  const [toast, setToast] = useState(null);

  const notify = useCallback((message, tone = "ok") => {
    setToast({ message, tone, id: Date.now() });
  }, []);

  const load = useCallback(async () => {
    try {
      const [list, kpis] = await Promise.all([api.listVehicles({ status: statusFilter, q: query }), api.stats()]);
      setVehicles(list);
      setStats(kpis);
      setError(null);
    } catch (err) {
      setError(err.message || "Backend unreachable");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, query]);

  useEffect(() => {
    load();
    const timer = setInterval(load, REFRESH_MS);
    return () => clearInterval(timer);
  }, [load]);

  const visible = useMemo(() => {
    const filtered = stateFilter ? vehicles.filter((v) => v.service_state === stateFilter) : vehicles;
    return sortByUrgency(filtered);
  }, [vehicles, stateFilter]);

  async function handleSave(data, existing) {
    try {
      if (existing) {
        await api.updateVehicle(existing.id, data);
        notify(`${data.name || existing.name} updated`);
      } else {
        await api.createVehicle(data);
        notify(`${data.name} registered`);
      }
      setModal(null);
      await load();
    } catch (err) {
      notify(err.message, "danger");
    }
  }

  async function handleDelete(vehicle) {
    try {
      await api.deleteVehicle(vehicle.id);
      notify(`${vehicle.name} removed`, "warn");
      if (drawerVehicle?.id === vehicle.id) setDrawerVehicle(null);
      await load();
    } catch (err) {
      notify(err.message, "danger");
    }
  }

  async function handleQuickOdometer(vehicle, delta) {
    try {
      await api.updateVehicle(vehicle.id, { odometer_km: vehicle.odometer_km + delta });
      await load();
    } catch (err) {
      notify(err.message, "danger");
    }
  }

  return (
    <div className="shell">
      <Sidebar stats={stats} stateFilter={stateFilter} onStateFilter={setStateFilter} />

      <main className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Fleet overview</p>
            <h1>Maintenance dashboard</h1>
          </div>
          <div className="topbar-actions">
            <span className={`pill ${error ? "pill-danger" : "pill-ok"}`}>
              <span className="dot" /> {error ? "Backend offline" : "Backend online"}
            </span>
            <button className="btn btn-primary" onClick={() => setModal({ mode: "create" })}>
              + Register vehicle
            </button>
          </div>
        </header>

        <KpiGrid stats={stats} loading={loading} />

        <section className="toolbar">
          <input
            className="input search"
            placeholder="Search by name or plate…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search vehicles"
          />
          <div className="segmented" role="tablist" aria-label="Status filter">
            {["", "ACTIVE", "IN_SHOP", "RETIRED"].map((s) => (
              <button
                key={s || "all"}
                role="tab"
                aria-selected={statusFilter === s}
                className={statusFilter === s ? "active" : ""}
                onClick={() => setStatusFilter(s)}
              >
                {s ? s.replace("_", " ") : "ALL"}
              </button>
            ))}
          </div>
        </section>

        {error && (
          <div className="banner banner-danger">
            <strong>Cannot reach the API.</strong> {error}. The dashboard will retry automatically.
          </div>
        )}

        {loading ? (
          <div className="grid">
            {Array.from({ length: 6 }).map((_, i) => (
              <div className="card skeleton" key={i} />
            ))}
          </div>
        ) : visible.length === 0 ? (
          <div className="empty">
            <h3>No vehicles match</h3>
            <p>Register your first vehicle or clear the filters to see the whole fleet.</p>
            <button className="btn btn-primary" onClick={() => setModal({ mode: "create" })}>
              Register vehicle
            </button>
          </div>
        ) : (
          <div className="grid">
            {visible.map((v) => (
              <VehicleCard
                key={v.id}
                vehicle={v}
                onEdit={() => setModal({ mode: "edit", vehicle: v })}
                onDelete={() => handleDelete(v)}
                onHistory={() => setDrawerVehicle(v)}
                onOdometer={(delta) => handleQuickOdometer(v, delta)}
              />
            ))}
          </div>
        )}
      </main>

      {modal && (
        <VehicleModal
          vehicle={modal.mode === "edit" ? modal.vehicle : null}
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}

      {drawerVehicle && (
        <ServiceDrawer
          vehicle={vehicles.find((v) => v.id === drawerVehicle.id) || drawerVehicle}
          onClose={() => setDrawerVehicle(null)}
          onChanged={load}
          notify={notify}
        />
      )}

      {toast && <Toast key={toast.id} {...toast} onDone={() => setToast(null)} />}
    </div>
  );
}
