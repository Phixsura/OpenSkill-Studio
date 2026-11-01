from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_infra_health_v9 import fleet_infra_health_v9
def test_ih2_v9():
    r = fleet_infra_health_v9([{"healthy": True, "degraded": False}])
    assert r["health_score"] == 100.0
    assert r["all_healthy"]
