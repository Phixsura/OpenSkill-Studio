from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_health_v9 import fleet_service_health_v9
def test_sh_v9():
    r = fleet_service_health_v9([{"healthy": True, "degraded": False, "down": False}])
    assert r["uptime_pct"] == 100.0
    assert r["all_healthy"]
