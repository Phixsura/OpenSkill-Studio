from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rate_limit_dashboard_v9 import fleet_rate_limit_dashboard_v9
def test_rld_v9():
    r = fleet_rate_limit_dashboard_v9([{"rps_limit": 10000, "throttled_today": 5, "any_consumer_limited": False}])
    assert r["throttled_today"] == 5
    assert r["healthy"]
