from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VehicleType(StrEnum):
    VAN = "VAN"
    TRUCK = "TRUCK"
    CAR = "CAR"
    BIKE = "BIKE"


class VehicleStatus(StrEnum):
    ACTIVE = "ACTIVE"
    IN_SHOP = "IN_SHOP"
    RETIRED = "RETIRED"


class ServiceType(StrEnum):
    OIL_CHANGE = "OIL_CHANGE"
    TIRES = "TIRES"
    BRAKES = "BRAKES"
    INSPECTION = "INSPECTION"
    REPAIR = "REPAIR"
    OTHER = "OTHER"


class ServiceState(StrEnum):
    OK = "OK"
    DUE_SOON = "DUE_SOON"
    OVERDUE = "OVERDUE"


def _normalize_plate(value: str) -> str:
    return " ".join(value.upper().split())


class VehicleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Van 12"])
    plate: str = Field(min_length=2, max_length=20, examples=["MH 12 AB 1234"])
    vehicle_type: VehicleType = VehicleType.VAN
    status: VehicleStatus = VehicleStatus.ACTIVE
    odometer_km: int = Field(default=0, ge=0)
    service_interval_km: int = Field(default=10_000, gt=0, le=200_000)
    last_service_km: int = Field(default=0, ge=0)

    @field_validator("plate")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        return _normalize_plate(value)


class VehicleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    plate: str | None = Field(default=None, min_length=2, max_length=20)
    vehicle_type: VehicleType | None = None
    status: VehicleStatus | None = None
    odometer_km: int | None = Field(default=None, ge=0)
    service_interval_km: int | None = Field(default=None, gt=0, le=200_000)
    last_service_km: int | None = Field(default=None, ge=0)

    @field_validator("plate")
    @classmethod
    def normalize_plate(cls, value: str | None) -> str | None:
        return _normalize_plate(value) if value is not None else None


class VehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    plate: str
    vehicle_type: VehicleType
    status: VehicleStatus
    odometer_km: int
    service_interval_km: int
    last_service_km: int
    last_service_at: datetime | None
    km_until_service: int
    service_state: ServiceState
    created_at: datetime
    updated_at: datetime


class ServiceRecordCreate(BaseModel):
    service_type: ServiceType = ServiceType.INSPECTION
    odometer_km: int = Field(ge=0)
    cost: float = Field(default=0, ge=0, le=1_000_000)
    notes: str = Field(default="", max_length=2000)
    performed_at: datetime | None = None


class ServiceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    service_type: ServiceType
    odometer_km: int
    cost: float
    notes: str
    performed_at: datetime
    created_at: datetime


class FleetStats(BaseModel):
    total_vehicles: int
    active: int
    in_shop: int
    retired: int
    ok: int
    due_soon: int
    overdue: int
    total_odometer_km: int
    service_records_total: int
    maintenance_cost_30d: float
    by_type: dict[str, int]
