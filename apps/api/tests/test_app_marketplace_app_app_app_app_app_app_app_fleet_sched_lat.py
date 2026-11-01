from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sched_lat import fleet_scheduling_latency
def test_sched():
    r = fleet_scheduling_latency([{"schedule_ms": 500}, {"schedule_ms": 1000}, {"schedule_ms": 8000}])
    assert r["avg_ms"] == 3166.7
    assert r["slow_scheduling"] == 1
    assert not r["fast"]
