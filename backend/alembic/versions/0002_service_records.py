"""add service_records table and last-service tracking on vehicles

Revision ID: 0002_service_records
Revises: 0001_create_vehicles
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_service_records"
down_revision = "0001_create_vehicles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vehicles", sa.Column("last_service_km", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("vehicles", sa.Column("last_service_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "service_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_type", sa.String(length=30), nullable=False, server_default="INSPECTION"),
        sa.Column("odometer_km", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_service_records_vehicle_id", "service_records", ["vehicle_id"])


def downgrade() -> None:
    op.drop_index("ix_service_records_vehicle_id", table_name="service_records")
    op.drop_table("service_records")
    op.drop_column("vehicles", "last_service_at")
    op.drop_column("vehicles", "last_service_km")
