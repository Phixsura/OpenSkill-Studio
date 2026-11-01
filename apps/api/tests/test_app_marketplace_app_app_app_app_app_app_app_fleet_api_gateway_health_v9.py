from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_gateway_health_v9 import fleet_api_gateway_health_v9
def test_agwh_v9():
    r = fleet_api_gateway_health_v9([{"healthy": True, "rps": 100000, "latency_ms": 5}])
    assert r["all_healthy"]
