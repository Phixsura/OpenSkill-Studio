from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_throttle import fleet_throttle_monitor
def test_throttle():
    r = fleet_throttle_monitor([{"throttled_pct": 0}, {"throttled_pct": 5}, {"throttled_pct": 15}])
    assert r["throttled"] == 2
    assert r["heavy"] == 1
    assert not r["clean"]
