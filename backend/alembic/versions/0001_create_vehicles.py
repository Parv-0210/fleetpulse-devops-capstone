"""create vehicles table

Revision ID: 0001_create_vehicles
Revises: None
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_create_vehicles"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("plate", sa.String(length=20), nullable=False),
        sa.Column("vehicle_type", sa.String(length=20), nullable=False, server_default="VAN"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("odometer_km", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("service_interval_km", sa.Integer(), nullable=False, server_default="10000"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_vehicles_plate", "vehicles", ["plate"], unique=True)
    op.create_index("ix_vehicles_status", "vehicles", ["status"])


def downgrade() -> None:
    op.drop_index("ix_vehicles_status", table_name="vehicles")
    op.drop_index("ix_vehicles_plate", table_name="vehicles")
    op.drop_table("vehicles")
