from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_quota_enforcement_v9 import fleet_api_quota_enforcement_v9
def test_aqe_v9():
    r = fleet_api_quota_enforcement_v9([{"quota_enforced": True, "quota_exceeded": False, "calls_today": 50000}])
    assert r["exceeded"] == 0
    assert r["healthy"]
