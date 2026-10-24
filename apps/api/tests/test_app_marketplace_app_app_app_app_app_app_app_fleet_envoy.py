from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_envoy import fleet_envoy_status
def test_envoy():
    r = fleet_envoy_status([{"live": True, "rps": 5000}, {"live": True, "draining": True, "rps": 1000}])
    assert r["live"] == 2
    assert r["draining"] == 1
    assert r["total_rps"] == 6000
