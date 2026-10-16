const ITEMS = [
  { key: "", label: "All vehicles", countKey: "total_vehicles" },
  { key: "OK", label: "Healthy", countKey: "ok", tone: "ok" },
  { key: "DUE_SOON", label: "Due soon", countKey: "due_soon", tone: "warn" },
  { key: "OVERDUE", label: "Overdue", countKey: "overdue", tone: "danger" },
];

export default function Sidebar({ stats, stateFilter, onStateFilter }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 64 64" width="22" height="22">
            <path d="M12 38h8l6-12h14l6 12h6" fill="none" stroke="currentColor" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="22" cy="44" r="5" fill="currentColor" />
            <circle cx="44" cy="44" r="5" fill="currentColor" />
          </svg>
        </span>
        <div>
          <strong>FleetPulse</strong>
          <small>maintenance control</small>
        </div>
      </div>

      <nav className="nav" aria-label="Maintenance state">
        <p className="nav-title">Fleet</p>
        {ITEMS.map((it) => (
          <button
            key={it.key || "all"}
            className={`nav-item ${stateFilter === it.key ? "active" : ""}`}
            onClick={() => onStateFilter(it.key)}
            aria-current={stateFilter === it.key ? "page" : undefined}
          >
            <span className={`swatch swatch-${it.tone || "neutral"}`} />
            {it.label}
            <span className="count">{stats?.[it.countKey] ?? "–"}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <a href="/docs" target="_blank" rel="noreferrer">API documentation</a>
        <span>v1.0.0</span>
      </div>
    </aside>
  );
}
