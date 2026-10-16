from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import FleetStats
from ..services import fleet_stats

router = APIRouter(prefix="/api/fleet", tags=["fleet"])


@router.get("/stats", response_model=FleetStats, summary="Fleet KPIs for the dashboard")
def stats(db: Session = Depends(get_db)):
    return fleet_stats(db)
