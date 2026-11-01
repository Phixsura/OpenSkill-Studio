from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_usage_quota_v9 import fleet_api_usage_quota_v9
def test_auq_v9():
    r = fleet_api_usage_quota_v9([{"usage_pct": 50, "calls_today": 50000}])
    assert r["over_quota"] == 0
    assert r["healthy"]
