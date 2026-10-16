def test_create_vehicle_normalizes_plate_and_derives_state(client, vehicle_payload):
    response = client.post("/api/vehicles", json=vehicle_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["plate"] == "MH 12 AB 1234"
    assert body["km_until_service"] == 6_000
    assert body["service_state"] == "OK"
    assert body["status"] == "ACTIVE"


def test_create_vehicle_rejects_invalid_payload(client):
    response = client.post("/api/vehicles", json={"name": "", "plate": "X", "odometer_km": -5})
    assert response.status_code == 422
    fields = {err["loc"][-1] for err in response.json()["detail"]}
    assert {"name", "plate", "odometer_km"} <= fields


def test_duplicate_plate_returns_409(client, vehicle, vehicle_payload):
    response = client.post("/api/vehicles", json={**vehicle_payload, "name": "Van 13"})
    assert response.status_code == 409


def test_list_vehicles_with_filters(client, vehicle_payload):
    client.post("/api/vehicles", json=vehicle_payload)
    client.post(
        "/api/vehicles",
        json={**vehicle_payload, "name": "Truck 7", "plate": "GJ 01 ZZ 9999", "status": "IN_SHOP"},
    )

    assert len(client.get("/api/vehicles").json()) == 2
    in_shop = client.get("/api/vehicles", params={"status": "IN_SHOP"}).json()
    assert [v["name"] for v in in_shop] == ["Truck 7"]
    search = client.get("/api/vehicles", params={"q": "mh 12"}).json()
    assert [v["name"] for v in search] == ["Van 12"]


def test_get_vehicle_by_id_and_404(client, vehicle):
    assert client.get(f"/api/vehicles/{vehicle['id']}").json()["id"] == vehicle["id"]
    assert client.get("/api/vehicles/999999").status_code == 404


def test_update_vehicle_odometer_changes_service_state(client, vehicle):
    response = client.put(f"/api/vehicles/{vehicle['id']}", json={"odometer_km": 29_700})
    assert response.status_code == 200
    assert response.json()["service_state"] == "DUE_SOON"
    assert response.json()["km_until_service"] == 300

    response = client.put(f"/api/vehicles/{vehicle['id']}", json={"odometer_km": 31_000, "status": "IN_SHOP"})
    assert response.json()["service_state"] == "OVERDUE"
    assert response.json()["status"] == "IN_SHOP"


def test_update_vehicle_with_empty_body_is_rejected(client, vehicle):
    assert client.put(f"/api/vehicles/{vehicle['id']}", json={}).status_code == 422


def test_delete_vehicle(client, vehicle):
    assert client.delete(f"/api/vehicles/{vehicle['id']}").status_code == 204
    assert client.get(f"/api/vehicles/{vehicle['id']}").status_code == 404
    assert client.delete(f"/api/vehicles/{vehicle['id']}").status_code == 404
