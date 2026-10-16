from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    plate: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(20), nullable=False, default="VAN")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", index=True)
    odometer_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    service_interval_km: Mapped[int] = mapped_column(Integer, nullable=False, default=10_000)
    last_service_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_service_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    services: Mapped[list["ServiceRecord"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan", order_by="ServiceRecord.performed_at.desc()"
    )


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(30), nullable=False, default="INSPECTION")
    odometer_km: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    vehicle: Mapped[Vehicle] = relationship(back_populates="services")
