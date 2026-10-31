from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_quota_v9 import fleet_service_quota_v9
def test_sq_v9():
    r = fleet_service_quota_v9([{"usage_pct": 50}, {"usage_pct": 60}])
    assert r["at_limit"] == 0
    assert r["healthy"]
