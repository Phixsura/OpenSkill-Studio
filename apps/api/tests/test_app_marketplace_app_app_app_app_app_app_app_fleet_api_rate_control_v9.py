from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_rate_control_v9 import fleet_api_rate_control_v9
def test_arc2_v9():
    r = fleet_api_rate_control_v9([{"adaptive": True, "throttled_today": 10}])
    assert r["adaptive"] == 1
    assert r["healthy"]
