from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_performance_v9 import fleet_api_performance_v9
def test_aperf_v9():
    r = fleet_api_performance_v9([{"within_sla": True, "response_ms": 25, "rps": 10000}])
    assert r["within_sla"] == 1
    assert r["healthy"]
