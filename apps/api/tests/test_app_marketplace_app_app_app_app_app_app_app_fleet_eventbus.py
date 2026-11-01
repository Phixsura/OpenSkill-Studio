from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_eventbus import fleet_eventbus_stats
def test_eventbus():
    r = fleet_eventbus_stats([{"events_per_sec": 1000, "lag_ms": 100}, {"events_per_sec": 2000, "lag_ms": 6000}])
    assert r["total_eps"] == 3000
    assert r["max_lag_ms"] == 6000
    assert r["lagging"]
