import { formatKm, humanize, intervalUsedPct, relativeDate, stateMeta } from "../lib/service.js";

export default function VehicleTable({ vehicles, onEdit, onDelete, onHistory }) {
  return (
    <div className="table-card">
      <div className="table-scroll">
        <table className="table">
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Type</th>
              <th>Status</th>
              <th className="num">Odometer</th>
              <th>Next service</th>
              <th>Last service</th>
              <th className="actions-col">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map((v) => {
              const meta = stateMeta(v.service_state);
              const pct = intervalUsedPct(v);
              const remaining =
                v.km_until_service <= 0
                  ? `${formatKm(-v.km_until_service)} overdue`
                  : `in ${formatKm(v.km_until_service)}`;
              return (
                <tr key={v.id}>
                  <td>
                    <div className="cell-title">{v.name}</div>
                    <div className="cell-sub mono">{v.plate}</div>
                  </td>
                  <td>{humanize(v.vehicle_type)}</td>
                  <td>
                    <span className={`status status-${v.status.toLowerCase()}`}>{humanize(v.status)}</span>
                  </td>
                  <td className="num">{formatKm(v.odometer_km)}</td>
                  <td>
                    <div className="next-service">
                      <span className={`badge badge-${meta.tone}`}>{meta.label}</span>
                      <span className="cell-sub">{remaining}</span>
                    </div>
                    <div className="meter" title={`${pct}% of the ${formatKm(v.service_interval_km)} interval used`}>
                      <span className={`meter-fill meter-${meta.tone}`} style={{ width: `${pct}%` }} />
                    </div>
                  </td>
                  <td className="cell-sub">{relativeDate(v.last_service_at)}</td>
                  <td className="actions-col">
                    <div className="row-actions">
                      <button className="btn btn-sm btn-secondary" onClick={() => onHistory(v)}>
                        Service log
                      </button>
                      <button className="btn btn-sm btn-secondary" onClick={() => onEdit(v)}>
                        Edit
                      </button>
                      <button className="btn btn-sm btn-ghost-danger" onClick={() => onDelete(v)} aria-label={`Remove ${v.name}`}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="table-footer">
        Showing {vehicles.length} vehicle{vehicles.length === 1 ? "" : "s"}, most urgent first
      </div>
    </div>
  );
}
