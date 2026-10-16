export default function Sidebar({ stats, stateFilter, onStateFilter }) {
  const items = [
    { key: "", label: "All vehicles", count: stats?.total_vehicles },
    { key: "OK", label: "Healthy", count: stats?.ok, tone: "ok" },
    { key: "DUE_SOON", label: "Due soon", count: stats?.due_soon, tone: "warn" },
    { key: "OVERDUE", label: "Overdue", count: stats?.overdue, tone: "danger" },
  ];
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 64 64" width="28" height="28">
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

      <nav className="nav">
        <p className="nav-title">Service state</p>
        {items.map((it) => (
          <button
            key={it.key || "all"}
            className={`nav-item ${stateFilter === it.key ? "active" : ""}`}
            onClick={() => onStateFilter(it.key)}
          >
            <span className={`swatch swatch-${it.tone || "neutral"}`} />
            {it.label}
            <span className="count">{it.count ?? "–"}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p className="nav-title">Pipeline</p>
        <ol className="pipeline">
          <li>Git push</li>
          <li>pytest + ruff</li>
          <li>Docker build</li>
          <li>Trivy scan</li>
          <li>GHCR push</li>
          <li>Helm deploy</li>
        </ol>
      </div>
    </aside>
  );
}
