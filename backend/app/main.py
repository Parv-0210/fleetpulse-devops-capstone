import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from . import __version__
from .config import settings
from .db import SessionLocal
from .metrics import register_fleet_collector
from .routes import fleet, services, system, vehicles

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

DESCRIPTION = """
FleetPulse keeps track of a vehicle fleet and its maintenance schedule.

* Register vehicles and keep their odometer current.
* Log service records (oil change, tyres, brakes, ...) which reset the maintenance counter.
* Every vehicle reports `km_until_service` and a `service_state` of **OK**, **DUE_SOON** or **OVERDUE**.
* `/api/fleet/stats` powers the dashboard; `/metrics` powers Prometheus and Grafana.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is owned by Alembic (see backend/alembic). Nothing to create here.
    logging.getLogger("fleetpulse").info("%s %s starting (env=%s)", settings.app_name, __version__, settings.app_env)
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=DESCRIPTION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(vehicles.router)
app.include_router(services.router)
app.include_router(fleet.router)

Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics", "/health", "/ready"],
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

fleet_collector = register_fleet_collector(SessionLocal)
