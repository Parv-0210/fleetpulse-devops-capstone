from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from .. import __version__
from ..config import settings
from ..db import get_db

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
    """Deeper check: a round-trip to the database succeeds, so this pod can take traffic."""
    db.execute(text("SELECT 1"))
    return {"status": "READY", "database": "ok"}
