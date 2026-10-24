from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sse import fleet_sse_metrics
def test_sse():
    r = fleet_sse_metrics([{"active_connections": 500, "events_per_sec": 5000}, {"active_connections": 300, "events_per_sec": 8000}])
    assert r["active_connections"] == 800
    assert r["events_per_sec"] == 13000
    assert r["high_volume"]
