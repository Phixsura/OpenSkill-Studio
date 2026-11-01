from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_quota_mgr_v9 import fleet_quota_mgr_v9
def test_quota_v9():
    r = fleet_quota_mgr_v9([{"usage_pct": 60}, {"usage_pct": 45}])
    assert r["over_quota"] == 0
    assert r["avg_usage_pct"] == 52.5
    assert r["healthy"]
