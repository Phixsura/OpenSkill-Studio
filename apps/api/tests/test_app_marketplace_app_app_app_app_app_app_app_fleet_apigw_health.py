from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_apigw_health import fleet_apigw_health
def test_gw():
    r = fleet_apigw_health([{"status": "healthy", "rps": 5000, "latency_ms": 10}, {"status": "degraded", "rps": 3000, "latency_ms": 50}])
    assert r["healthy"] == 1
    assert r["total_rps"] == 8000
    assert not r["all_healthy"]
