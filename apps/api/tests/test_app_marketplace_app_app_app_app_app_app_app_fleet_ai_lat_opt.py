from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_lat_opt import fleet_ai_latency_optimizer
def test_lo():
    r = fleet_ai_latency_optimizer([{"active": True, "p50_ms": 50, "p99_ms": 150, "optimizations_applied": 10}])
    assert r["p99_ms"] == 150.0
    assert r["fast"]
