import { formatMoney } from "../lib/service.js";

function Kpi({ label, value, hint, tone }) {
  return (
    <div className={`kpi kpi-${tone || "neutral"}`}>
      <p className="kpi-label">{label}</p>
      <p className="kpi-value">{value}</p>
      {hint && <p className="kpi-hint">{hint}</p>}
    </div>
  );
}

export default function KpiGrid({ stats, loading }) {
  if (loading || !stats) {
    return (
      <section className="kpis">
        {Array.from({ length: 5 }).map((_, i) => (
          <div className="kpi skeleton" key={i} />
        ))}
      </section>
    );
  }
  const attention = stats.due_soon + stats.overdue;
  return (
    <section className="kpis">
      <Kpi label="Fleet size" value={stats.total_vehicles} hint={`${stats.active} active · ${stats.in_shop} in shop`} />
      <Kpi
        label="Needs attention"
        value={attention}
        hint={`${stats.overdue} overdue · ${stats.due_soon} due soon`}
        tone={stats.overdue ? "danger" : attention ? "warn" : "ok"}
      />
      <Kpi label="Healthy" value={stats.ok} hint="within service interval" tone="ok" />
      <Kpi label="Distance tracked" value={(stats.total_odometer_km || 0).toLocaleString("en-IN")} hint="km · sum of odometers" />
      <Kpi label="Spend · 30 days" value={formatMoney(stats.maintenance_cost_30d)} hint={`${stats.service_records_total} services logged`} />
    </section>
  );
}
