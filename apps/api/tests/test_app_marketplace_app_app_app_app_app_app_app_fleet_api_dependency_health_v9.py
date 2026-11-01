from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_dependency_health_v9 import fleet_api_dependency_health_v9
def test_adh3_v9():
    r = fleet_api_dependency_health_v9([{"healthy": True, "degraded": False, "down": False, "latency_ms": 10}])
    assert r["all_healthy"]
