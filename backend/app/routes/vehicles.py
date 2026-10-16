from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..metrics import SERVICE_RECORDS_CREATED
from ..models import ServiceRecord, Vehicle
from ..schemas import (
    ServiceRecordCreate,
    ServiceRecordOut,
    VehicleCreate,
    VehicleOut,
    VehicleStatus,
    VehicleUpdate,
)
from ..services import apply_service_record, enrich

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


def _get_or_404(db: Session, vehicle_id: int) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.get("", response_model=list[VehicleOut], summary="List vehicles")
def list_vehicles(
    db: Session = Depends(get_db),
    status_filter: VehicleStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, max_length=100, description="Search by name or plate"),
):
    stmt = select(Vehicle).order_by(Vehicle.id.desc())
    if status_filter:
        stmt = stmt.where(Vehicle.status == status_filter.value)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Vehicle.name.ilike(like), Vehicle.plate.ilike(like)))
    return [enrich(v) for v in db.scalars(stmt)]


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED, summary="Register a vehicle")
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Plate '{payload.plate}' is already registered") from None
    db.refresh(vehicle)
    return enrich(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleOut, summary="Get one vehicle")
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return enrich(_get_or_404(db, vehicle_id))


@router.put("/{vehicle_id}", response_model=VehicleOut, summary="Update a vehicle")
def update_vehicle(vehicle_id: int, payload: VehicleUpdate, db: Session = Depends(get_db)):
    vehicle = _get_or_404(db, vehicle_id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No fields to update")
    for key, value in changes.items():
        setattr(vehicle, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Plate is already registered") from None
    db.refresh(vehicle)
    return enrich(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove a vehicle")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = _get_or_404(db, vehicle_id)
    db.delete(vehicle)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{vehicle_id}/services", response_model=list[ServiceRecordOut], summary="Service history")
def list_services(vehicle_id: int, db: Session = Depends(get_db)):
    _get_or_404(db, vehicle_id)
    stmt = (
        select(ServiceRecord)
        .where(ServiceRecord.vehicle_id == vehicle_id)
        .order_by(ServiceRecord.performed_at.desc(), ServiceRecord.id.desc())
    )
    return list(db.scalars(stmt))


@router.post(
    "/{vehicle_id}/services",
    response_model=ServiceRecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log a maintenance service",
)
def create_service(vehicle_id: int, payload: ServiceRecordCreate, db: Session = Depends(get_db)):
    vehicle = _get_or_404(db, vehicle_id)
    data = payload.model_dump(exclude_none=True)
    record = ServiceRecord(vehicle_id=vehicle.id, **data)
    db.add(record)
    db.flush()  # populate defaults such as performed_at before we use them
    apply_service_record(vehicle, record)
    db.commit()
    db.refresh(record)
    SERVICE_RECORDS_CREATED.labels(service_type=record.service_type).inc()
    return record
