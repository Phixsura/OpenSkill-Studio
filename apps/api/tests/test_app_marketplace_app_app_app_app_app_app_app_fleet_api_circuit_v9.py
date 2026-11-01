from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_circuit_v9 import fleet_api_circuit_v9
def test_acir_v9():
    r = fleet_api_circuit_v9([{"state": "closed", "trips_today": 0}])
    assert r["closed"] == 1
    assert r["healthy"]
