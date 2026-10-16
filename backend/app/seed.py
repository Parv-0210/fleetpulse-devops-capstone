"""Seed demo vehicles so a fresh environment has something to show.

Idempotent: does nothing when the vehicles table already has rows.
Run with: python -m app.seed
"""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from .db import SessionLocal
from .models import ServiceRecord, Vehicle

log = logging.getLogger("fleetpulse.seed")

DEMO_VEHICLES = [
    # name, plate, type, status, odometer, interval, last_service_km, days since service, last cost
    ("Van 12", "MH 12 AB 1234", "VAN", "ACTIVE", 24_300, 10_000, 20_000, 42, 3_200),
    ("Van 07", "MH 14 CD 0077", "VAN", "ACTIVE", 39_650, 10_000, 30_000, 95, 2_750),
    ("Truck Alpha", "GJ 01 TR 9001", "TRUCK", "ACTIVE", 128_900, 15_000, 112_000, 130, 18_400),
    ("Truck Bravo", "GJ 01 TR 9002", "TRUCK", "IN_SHOP", 141_200, 15_000, 125_500, 160, 9_900),
    ("Pool Car 3", "KA 05 PC 0003", "CAR", "ACTIVE", 17_480, 8_000, 16_000, 20, 1_900),
    ("Courier Bike 9", "DL 3C BK 0009", "BIKE", "ACTIVE", 9_120, 3_000, 6_200, 61, 650),
    ("Van 02 (old)", "MH 12 AB 0002", "VAN", "RETIRED", 211_000, 10_000, 205_000, 400, 4_100),
]


def seed() -> int:
    with SessionLocal() as db:
        existing = db.scalar(select(func.count(Vehicle.id))) or 0
        if existing:
            log.info("seed skipped: %d vehicles already present", existing)
            return 0
        now = datetime.now(UTC)
        for name, plate, vtype, status, odo, interval, last_km, days_ago, cost in DEMO_VEHICLES:
            performed = now - timedelta(days=days_ago)
            vehicle = Vehicle(
                name=name,
                plate=plate,
                vehicle_type=vtype,
                status=status,
                odometer_km=odo,
                service_interval_km=interval,
                last_service_km=last_km,
                last_service_at=performed,
            )
            vehicle.services.append(
                ServiceRecord(
                    service_type="INSPECTION",
                    odometer_km=last_km,
                    cost=cost,
                    notes="Scheduled service (demo data)",
                    performed_at=performed,
                )
            )
            db.add(vehicle)
        db.commit()
        log.info("seeded %d demo vehicles", len(DEMO_VEHICLES))
        return len(DEMO_VEHICLES)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    seed()
