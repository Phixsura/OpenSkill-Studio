from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_webhook_transform_v9 import fleet_webhook_transform_v9
def test_wt_v9():
    r = fleet_webhook_transform_v9([{"active": True, "transformed_today": 5000, "errors": 0}])
    assert r["transformed_today"] == 5000
    assert r["healthy"]
