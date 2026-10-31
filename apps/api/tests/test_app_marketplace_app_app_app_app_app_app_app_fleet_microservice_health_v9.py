from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_microservice_health_v9 import fleet_microservice_health_v9
def test_msh_v9():
    r = fleet_microservice_health_v9([{"healthy": True, "degraded": False, "critical": False, "latency_ms": 25}])
    assert r["all_healthy"]
