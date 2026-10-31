from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_throttle_v9 import fleet_api_throttle_v9
def test_at2_v9():
    r = fleet_api_throttle_v9([{"throttled": False, "requests_today": 100000}])
    assert r["throttle_rate_pct"] == 0.0
    assert r["healthy"]
