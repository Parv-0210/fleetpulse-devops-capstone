from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import __version__
from ..config import settings
from ..db import get_db
from ..models import Vehicle

router = APIRouter(tags=["system"])


@router.get("/", summary="Service banner")
def root():
    return {"service": settings.app_name, "version": __version__, "env": settings.app_env, "docs": "/docs"}


@router.get("/health", summary="Liveness probe")
def health():
    """Cheap check: the process is up and can answer HTTP."""
    return {"status": "UP"}


@router.get("/ready", summary="Readiness probe")
def ready(db: Session = Depends(get_db)):
    """Deeper check: the database answers *and* the schema has been migrated.

    Querying the vehicles table (instead of a bare SELECT 1) keeps a pod out of the
    Service until the migration init step has finished, so no request can hit a
    half-initialised replica."""
    db.execute(select(Vehicle.id).limit(1)).first()
    return {"status": "READY", "database": "ok"}
