import { formatKm, humanize, intervalUsedPct, relativeDate, stateMeta } from "../lib/service.js";

const TYPE_ICON = { VAN: "🚐", TRUCK: "🚚", CAR: "🚗", BIKE: "🏍️" };

export default function VehicleCard({ vehicle, onEdit, onDelete, onHistory, onOdometer }) {
  const meta = stateMeta(vehicle.service_state);
  const pct = intervalUsedPct(vehicle);
  return (
    <article className={`card vehicle tone-${meta.tone}`}>
      <header className="card-head">
        <span className="type-icon" aria-hidden="true">{TYPE_ICON[vehicle.vehicle_type] || "🚘"}</span>
        <div className="card-title">
          <h3>{vehicle.name}</h3>
          <code className="plate">{vehicle.plate}</code>
        </div>
        <span className={`badge badge-${meta.tone}`}>{meta.label}</span>
      </header>

      <dl className="facts">
        <div>
          <dt>Odometer</dt>
          <dd>{formatKm(vehicle.odometer_km)}</dd>
        </div>
        <div>
          <dt>Next service</dt>
          <dd>{vehicle.km_until_service <= 0 ? `${formatKm(-vehicle.km_until_service)} overdue` : `in ${formatKm(vehicle.km_until_service)}`}</dd>
        </div>
        <div>
          <dt>Last service</dt>
          <dd>{relativeDate(vehicle.last_service_at)}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{humanize(vehicle.status)}</dd>
        </div>
      </dl>

      <div className="meter" title={`${pct}% of the ${formatKm(vehicle.service_interval_km)} interval used`}>
        <span className={`meter-fill meter-${meta.tone}`} style={{ width: `${pct}%` }} />
      </div>

      <footer className="card-actions">
        <div className="odo-buttons" aria-label="Quick odometer update">
          <button className="btn btn-ghost" onClick={() => onOdometer(100)}>+100 km</button>
          <button className="btn btn-ghost" onClick={() => onOdometer(1000)}>+1,000 km</button>
        </div>
        <div className="spacer" />
        <button className="btn btn-ghost" onClick={onHistory}>Service log</button>
        <button className="btn btn-ghost" onClick={onEdit}>Edit</button>
        <button className="btn btn-ghost btn-danger" onClick={onDelete}>Remove</button>
      </footer>
    </article>
  );
}
