from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_circuit_health_v9 import fleet_api_circuit_health_v9
def test_ach_v9():
    r = fleet_api_circuit_health_v9([{"state": "closed", "trips_24h": 2, "auto_recovered": 2}])
    assert r["closed"] == 1
    assert r["healthy"]
