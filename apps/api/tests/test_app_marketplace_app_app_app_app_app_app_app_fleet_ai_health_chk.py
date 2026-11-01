from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_health_chk import fleet_ai_health_check
def test_hc():
    r = fleet_ai_health_check([{"status": "healthy", "latency_ms": 5}, {"status": "healthy", "latency_ms": 8}])
    assert r["healthy"] == 2
    assert r["all_green"]
