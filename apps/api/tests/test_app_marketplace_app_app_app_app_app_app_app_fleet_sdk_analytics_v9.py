from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sdk_analytics_v9 import fleet_sdk_analytics_v9
def test_sdk2_v9():
    r = fleet_sdk_analytics_v9([{"language": "python", "downloads_today": 5000, "active_users": 500}])
    assert r["languages"] == 1
    assert r["healthy"]
