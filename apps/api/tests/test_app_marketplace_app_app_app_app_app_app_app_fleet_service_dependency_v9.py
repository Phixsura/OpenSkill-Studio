from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_dependency_v9 import fleet_service_dependency_v9
def test_sd2_v9():
    r = fleet_service_dependency_v9([{"healthy": True, "circular": False, "latency_ms": 5}])
    assert r["circular"] == 0
    assert r["all_healthy"]
