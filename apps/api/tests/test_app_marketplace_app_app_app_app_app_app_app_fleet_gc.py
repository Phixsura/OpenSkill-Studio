from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gc import fleet_gc_pressure
def test_gc():
    r = fleet_gc_pressure([{"gc_pause_ms": 100}, {"gc_pause_ms": 300}, {"gc_pause_ms": 500}])
    assert r["avg_gc_pause_ms"] == 300
    assert r["high_pressure"]
