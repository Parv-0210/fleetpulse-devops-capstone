def test_root_banner(client):
    body = client.get("/").json()
    assert body["service"] == "FleetPulse API"
    assert body["docs"] == "/docs"


def test_health_is_up(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY", "database": "ok"}


def test_openapi_lists_crud_routes(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "get" in paths["/api/vehicles"]
    assert "post" in paths["/api/vehicles"]
    assert "put" in paths["/api/vehicles/{vehicle_id}"]
    assert "delete" in paths["/api/vehicles/{vehicle_id}"]
