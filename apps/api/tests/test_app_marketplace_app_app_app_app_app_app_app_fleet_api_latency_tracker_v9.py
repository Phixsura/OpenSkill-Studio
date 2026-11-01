from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_latency_tracker_v9 import fleet_api_latency_tracker_v9
def test_alt_v9():
    r = fleet_api_latency_tracker_v9([{"p50_ms": 10, "p95_ms": 50, "p99_ms": 100}])
    assert r["avg_p99_ms"] == 100.0
    assert r["healthy"]
