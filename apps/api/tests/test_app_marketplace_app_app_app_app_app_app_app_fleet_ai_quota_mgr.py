from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_quota_mgr import fleet_ai_quota_manager
def test_qm():
    r = fleet_ai_quota_manager([{"active": True, "tenants": 500, "enforced": 500, "throttled_24h": 20}])
    assert r["tenants"] == 500
    assert r["fair"]
