from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_usage_analytics_v9 import fleet_api_usage_analytics_v9
def test_aua2_v9():
    r = fleet_api_usage_analytics_v9([{"trend": "growing", "calls_30d": 1000000}])
    assert r["growing"] == 1
    assert r["healthy"]
