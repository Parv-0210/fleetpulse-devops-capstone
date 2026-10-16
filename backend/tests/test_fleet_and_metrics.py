def test_fleet_stats_aggregate_states_and_cost(client, vehicle_payload):
    ok = client.post("/api/vehicles", json=vehicle_payload).json()
    client.post("/api/vehicles", json={**vehicle_payload, "plate": "KA 05 MM 0001", "odometer_km": 29_800})
    client.post(
        "/api/vehicles",
        json={
            **vehicle_payload,
            "plate": "KA 05 MM 0002",
            "odometer_km": 31_000,
            "status": "RETIRED",
            "vehicle_type": "TRUCK",
        },
    )
    client.post(f"/api/vehicles/{ok['id']}/services", json={"odometer_km": 24_500, "cost": 200})

    stats = client.get("/api/fleet/stats").json()
    assert stats["total_vehicles"] == 3
    assert stats["active"] == 2 and stats["retired"] == 1 and stats["in_shop"] == 0
    assert (stats["ok"], stats["due_soon"], stats["overdue"]) == (1, 1, 1)
    assert stats["service_records_total"] == 1
    assert stats["maintenance_cost_30d"] == 200.0
    assert stats["by_type"] == {"TRUCK": 1, "VAN": 2}


def test_metrics_endpoint_exposes_http_and_fleet_metrics(client, vehicle):
    client.get("/api/vehicles")
    client.post(f"/api/vehicles/{vehicle['id']}/services", json={"service_type": "REPAIR", "odometer_km": 24_100})

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    text = response.text
    assert "http_requests_total" in text
    assert 'fleetpulse_vehicles{status="ACTIVE"} 1.0' in text
    assert 'fleetpulse_vehicles_by_service_state{state="OK"} 1.0' in text
    assert 'fleetpulse_service_records_created_total{service_type="REPAIR"}' in text
