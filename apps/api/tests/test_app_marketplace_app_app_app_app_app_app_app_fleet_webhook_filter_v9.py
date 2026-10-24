from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_webhook_filter_v9 import fleet_webhook_filter_v9
def test_wf2_v9():
    r = fleet_webhook_filter_v9([{"active": True, "filtered_today": 5000, "passed_today": 10000}])
    assert r["passed_today"] == 10000
    assert r["healthy"]
