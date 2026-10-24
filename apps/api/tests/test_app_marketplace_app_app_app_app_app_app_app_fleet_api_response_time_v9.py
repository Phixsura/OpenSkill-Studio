from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_response_time_v9 import fleet_api_response_time_v9
def test_art2_v9():
    r = fleet_api_response_time_v9([{"within_sla": True, "avg_ms": 25, "p99_ms": 100}])
    assert r["within_sla"] == 1
    assert r["healthy"]
