def test_logging_service_resets_maintenance_counter(client, vehicle):
    response = client.post(
        f"/api/vehicles/{vehicle['id']}/services",
        json={"service_type": "OIL_CHANGE", "odometer_km": 25_000, "cost": 149.5, "notes": "5W-30"},
    )
    assert response.status_code == 201
    record = response.json()
    assert record["service_type"] == "OIL_CHANGE"
    assert record["cost"] == 149.5

    updated = client.get(f"/api/vehicles/{vehicle['id']}").json()
    assert updated["last_service_km"] == 25_000
    assert updated["odometer_km"] == 25_000  # odometer advanced to the service reading
    assert updated["km_until_service"] == 10_000
    assert updated["service_state"] == "OK"
    assert updated["last_service_at"] is not None


def test_service_history_is_newest_first(client, vehicle):
    url = f"/api/vehicles/{vehicle['id']}/services"
    client.post(url, json={"service_type": "TIRES", "odometer_km": 24_100, "performed_at": "2026-01-10T09:00:00Z"})
    client.post(url, json={"service_type": "BRAKES", "odometer_km": 24_500, "performed_at": "2026-03-01T09:00:00Z"})
    history = client.get(url).json()
    assert [r["service_type"] for r in history] == ["BRAKES", "TIRES"]


def test_service_validation_and_unknown_vehicle(client, vehicle):
    bad = client.post(f"/api/vehicles/{vehicle['id']}/services", json={"service_type": "WASH", "odometer_km": 1})
    assert bad.status_code == 422
    missing = client.post("/api/vehicles/424242/services", json={"odometer_km": 1})
    assert missing.status_code == 404


def test_delete_service_record(client, vehicle):
    record = client.post(f"/api/vehicles/{vehicle['id']}/services", json={"odometer_km": 24_200}).json()
    assert client.delete(f"/api/services/{record['id']}").status_code == 204
    assert client.get(f"/api/vehicles/{vehicle['id']}/services").json() == []
    assert client.delete(f"/api/services/{record['id']}").status_code == 404


def test_deleting_vehicle_cascades_to_services(client, vehicle):
    client.post(f"/api/vehicles/{vehicle['id']}/services", json={"odometer_km": 24_200})
    assert client.delete(f"/api/vehicles/{vehicle['id']}").status_code == 204
    assert client.get(f"/api/vehicles/{vehicle['id']}/services").status_code == 404
