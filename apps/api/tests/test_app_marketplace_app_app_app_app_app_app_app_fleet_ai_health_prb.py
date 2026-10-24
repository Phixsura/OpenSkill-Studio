from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_health_prb import fleet_ai_health_probe_v2
def test_hp():
    r = fleet_ai_health_probe_v2([{"active": True, "endpoints": 200, "checks_24h": 1000000, "deps": 50, "healthy": True}])
    assert r["endpoints"] == 200
    assert r["all_healthy"]
