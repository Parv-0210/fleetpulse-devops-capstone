"""Test fixtures.

Tests never touch the production database. They run against:
  * TEST_DATABASE_URL if set (CI uses a throw-away PostgreSQL service container), or
  * an in-memory SQLite database otherwise (fast local runs, no services needed).

The FastAPI `get_db` dependency is overridden so every request uses the test engine,
and the custom Prometheus collector is pointed at the same engine.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app, fleet_collector
from app.models import ServiceRecord, Vehicle

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")

if TEST_DATABASE_URL.startswith("sqlite"):
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
else:
    test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
fleet_collector.session_factory = TestingSessionLocal


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    """Each test starts from an empty database."""
    yield
    with TestingSessionLocal() as db:
        db.execute(delete(ServiceRecord))
        db.execute(delete(Vehicle))
        db.commit()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def vehicle_payload():
    return {
        "name": "Van 12",
        "plate": "mh 12 ab 1234",
        "vehicle_type": "VAN",
        "odometer_km": 24_000,
        "service_interval_km": 10_000,
        "last_service_km": 20_000,
    }


@pytest.fixture
def vehicle(client, vehicle_payload):
    response = client.post("/api/vehicles", json=vehicle_payload)
    assert response.status_code == 201
    return response.json()
