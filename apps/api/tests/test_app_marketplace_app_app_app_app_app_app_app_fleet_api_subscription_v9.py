from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_subscription_v9 import fleet_api_subscription_v9
def test_asub_v9():
    r = fleet_api_subscription_v9([{"active": True, "events_today": 10000, "failed_today": 0}])
    assert r["events_today"] == 10000
    assert r["healthy"]
