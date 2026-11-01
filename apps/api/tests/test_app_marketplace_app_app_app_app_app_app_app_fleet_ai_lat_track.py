from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_lat_track import fleet_ai_latency_tracker
def test_lt():
    r = fleet_ai_latency_tracker([{"active": True, "endpoints": 500, "p50_ms": 25, "p99_ms": 100}])
    assert r["endpoints"] == 500
    assert r["fast"]
