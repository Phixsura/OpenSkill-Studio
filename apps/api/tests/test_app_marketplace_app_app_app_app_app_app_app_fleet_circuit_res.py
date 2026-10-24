from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_circuit_res import fleet_circuit_resilience
def test_circuit():
    r = fleet_circuit_resilience([{"state": "closed", "trips_24h": 2, "recovery_sec": 30}, {"state": "closed", "trips_24h": 1, "recovery_sec": 60}])
    assert r["trips_24h"] == 3
    assert r["resilient"]
