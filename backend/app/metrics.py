"""Custom Prometheus metrics for FleetPulse.

The HTTP-level metrics (request count, latency, sizes) come from
prometheus-fastapi-instrumentator. This module adds *business* metrics:

- fleetpulse_vehicles{status}            gauge, computed at scrape time from the DB
- fleetpulse_vehicles_by_service_state{state}  gauge, OK / DUE_SOON / OVERDUE
- fleetpulse_service_records_created_total{service_type}  counter

Computing the gauges at scrape time (instead of caching in-process) keeps every
replica consistent when the Deployment runs more than one pod.
"""

import logging
from collections.abc import Callable, Iterable

from prometheus_client import REGISTRY, Counter
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Vehicle
from .schemas import ServiceState
from .services import service_state

log = logging.getLogger(__name__)

SERVICE_RECORDS_CREATED = Counter(
    "fleetpulse_service_records_created_total",
    "Number of maintenance records logged since the process started.",
    ["service_type"],
)


class FleetCollector(Collector):
    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def collect(self) -> Iterable[GaugeMetricFamily]:
        vehicles_by_status = GaugeMetricFamily(
            "fleetpulse_vehicles", "Vehicles in the fleet, by lifecycle status.", labels=["status"]
        )
        vehicles_by_state = GaugeMetricFamily(
            "fleetpulse_vehicles_by_service_state",
            "Vehicles grouped by maintenance state (OK, DUE_SOON, OVERDUE).",
            labels=["state"],
        )
        try:
            with self.session_factory() as db:
                rows = db.execute(select(Vehicle.status, func.count(Vehicle.id)).group_by(Vehicle.status)).all()
                counts = {status: count for status, count in rows}
                for status in ("ACTIVE", "IN_SHOP", "RETIRED"):
                    vehicles_by_status.add_metric([status], counts.get(status, 0))

                states = dict.fromkeys(ServiceState, 0)
                for vehicle in db.scalars(select(Vehicle)):
                    states[service_state(vehicle)] += 1
                for state, count in states.items():
                    vehicles_by_state.add_metric([state.value], count)
        except Exception as exc:  # pragma: no cover - only hit when the DB is unreachable
            log.warning("fleet metrics collection skipped: %s", exc)
            return []
        return [vehicles_by_status, vehicles_by_state]


def register_fleet_collector(session_factory: Callable[[], Session]) -> FleetCollector:
    collector = FleetCollector(session_factory)
    REGISTRY.register(collector)
    return collector
