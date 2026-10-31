from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_waf_v9 import fleet_cloud_waf_v9
def test_cwaf_v9():
    r = fleet_cloud_waf_v9([{"active": True, "blocked_today": 1000, "false_positives": 0}])
    assert r["blocked_today"] == 1000
    assert r["healthy"]
