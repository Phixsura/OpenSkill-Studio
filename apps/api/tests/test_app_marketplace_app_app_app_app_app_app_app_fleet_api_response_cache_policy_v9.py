from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_response_cache_policy_v9 import fleet_api_response_cache_policy_v9
def test_arcp_v9():
    r = fleet_api_response_cache_policy_v9([{"enabled": True, "hit_rate_pct": 90, "bytes_saved_mb": 1000}])
    assert r["avg_hit_rate"] == 90.0
    assert r["healthy"]
