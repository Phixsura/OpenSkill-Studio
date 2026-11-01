from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cpu_throttle import fleet_cpu_throttling
def test_throttle():
    r = fleet_cpu_throttling([{"throttled_pct": 0}, {"throttled_pct": 10}, {"throttled_pct": 50}])
    assert r["throttled"] == 2
    assert r["severe"] == 1
    assert not r["healthy"]
