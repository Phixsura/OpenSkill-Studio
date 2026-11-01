from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_xregion_lat import fleet_xregion_latency
def test_xregion():
    r = fleet_xregion_latency([{"latency_ms": 50}, {"latency_ms": 300}])
    assert r["avg_latency_ms"] == 175.0
    assert r["high_latency"] == 1
    assert not r["acceptable"]
