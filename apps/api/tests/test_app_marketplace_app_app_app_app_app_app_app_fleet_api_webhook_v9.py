from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_webhook_v9 import fleet_api_webhook_v9
def test_aw2_v9():
    r = fleet_api_webhook_v9([{"active": True, "delivered_today": 10000, "failed_today": 0}])
    assert r["delivered_today"] == 10000
    assert r["healthy"]
