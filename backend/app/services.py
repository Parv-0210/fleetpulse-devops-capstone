"""Domain logic that is independent of HTTP: maintenance state and fleet statistics."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .models import ServiceRecord, Vehicle
from .schemas import FleetStats, ServiceState


def km_until_service(vehicle: Vehicle) -> int:
    return vehicle.last_service_km + vehicle.service_interval_km - vehicle.odometer_km


def service_state(vehicle: Vehicle, due_soon_km: int | None = None) -> ServiceState:
    threshold = settings.service_due_soon_km if due_soon_km is None else due_soon_km
    remaining = km_until_service(vehicle)
    if remaining <= 0:
        return ServiceState.OVERDUE
    if remaining <= threshold:
        return ServiceState.DUE_SOON
    return ServiceState.OK


def enrich(vehicle: Vehicle) -> dict:
    """Attach derived fields so the response schema can be built from attributes."""
    vehicle.km_until_service = km_until_service(vehicle)  # type: ignore[attr-defined]
    vehicle.service_state = service_state(vehicle)  # type: ignore[attr-defined]
    return vehicle


def apply_service_record(vehicle: Vehicle, record: ServiceRecord) -> None:
    """A logged service resets the maintenance counter and can advance the odometer."""
    vehicle.last_service_km = record.odometer_km
    vehicle.last_service_at = record.performed_at
    if record.odometer_km > vehicle.odometer_km:
        vehicle.odometer_km = record.odometer_km


def fleet_stats(db: Session) -> FleetStats:
    vehicles = list(db.scalars(select(Vehicle)))
    status_counts = {"ACTIVE": 0, "IN_SHOP": 0, "RETIRED": 0}
    state_counts = {ServiceState.OK: 0, ServiceState.DUE_SOON: 0, ServiceState.OVERDUE: 0}
    by_type: dict[str, int] = {}
    total_km = 0
    for v in vehicles:
        status_counts[v.status] = status_counts.get(v.status, 0) + 1
        state_counts[service_state(v)] += 1
        by_type[v.vehicle_type] = by_type.get(v.vehicle_type, 0) + 1
        total_km += v.odometer_km

    since = datetime.now(UTC) - timedelta(days=30)
    cost_30d = db.scalar(
        select(func.coalesce(func.sum(ServiceRecord.cost), 0)).where(ServiceRecord.performed_at >= since)
    )
    records_total = db.scalar(select(func.count(ServiceRecord.id))) or 0

    return FleetStats(
        total_vehicles=len(vehicles),
        active=status_counts["ACTIVE"],
        in_shop=status_counts["IN_SHOP"],
        retired=status_counts["RETIRED"],
        ok=state_counts[ServiceState.OK],
        due_soon=state_counts[ServiceState.DUE_SOON],
        overdue=state_counts[ServiceState.OVERDUE],
        total_odometer_km=total_km,
        service_records_total=records_total,
        maintenance_cost_30d=float(cost_30d or 0),
        by_type=dict(sorted(by_type.items())),
    )
