from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_access_policy_v9 import fleet_api_access_policy_v9
def test_aap2_v9():
    r = fleet_api_access_policy_v9([{"enforced": True, "ip_restricted": True, "scope_limited": True}])
    assert r["enforced"] == 1
    assert r["healthy"]
