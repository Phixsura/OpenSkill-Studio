from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_composition_v9 import fleet_api_composition_v9
def test_ac3_v9():
    r = fleet_api_composition_v9([{"active": True, "backends": 3, "avg_latency_ms": 50}])
    assert r["total_backends"] == 3
    assert r["healthy"]
