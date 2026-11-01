from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_queue_wait import fleet_queue_wait
def test_wait():
    r = fleet_queue_wait([{"avg_wait_ms": 100, "p99_wait_ms": 2000}, {"avg_wait_ms": 200, "p99_wait_ms": 8000}])
    assert r["avg_wait_ms"] == 150.0
    assert r["p99_wait_ms"] == 8000
    assert not r["acceptable"]
