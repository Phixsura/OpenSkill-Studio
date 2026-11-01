from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_knative import fleet_knative_status
def test_kn():
    r = fleet_knative_status([{"ready": True, "cold_starts_24h": 50, "avg_latency_ms": 100}, {"ready": True, "cold_starts_24h": 30, "avg_latency_ms": 150}])
    assert r["cold_starts_24h"] == 80
    assert r["avg_latency_ms"] == 125.0
    assert r["all_ready"]
