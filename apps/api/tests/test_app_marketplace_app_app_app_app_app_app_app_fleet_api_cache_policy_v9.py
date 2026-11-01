from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_cache_policy_v9 import fleet_api_cache_policy_v9
def test_acpol_v9():
    r = fleet_api_cache_policy_v9([{"active": True, "ttl_sec": 300, "invalidations_today": 100}])
    assert r["avg_ttl_sec"] == 300.0
    assert r["healthy"]
