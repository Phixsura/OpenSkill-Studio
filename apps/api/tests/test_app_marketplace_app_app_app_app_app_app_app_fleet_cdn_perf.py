from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cdn_perf import fleet_cdn_perf
def test_cdn():
    r = fleet_cdn_perf([{"hits": 900, "misses": 100, "latency_ms": 20}, {"hits": 950, "misses": 50, "latency_ms": 30}])
    assert r["hit_rate_pct"] == 92.5
    assert r["effective"]
