from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloudrun import fleet_cloudrun_status
def test_cr():
    r = fleet_cloudrun_status([{"active": True, "revisions": 10, "requests_24h": 5000000, "avg_latency_ms": 50}])
    assert r["requests_24h"] == 5000000
    assert r["avg_latency_ms"] == 50.0
