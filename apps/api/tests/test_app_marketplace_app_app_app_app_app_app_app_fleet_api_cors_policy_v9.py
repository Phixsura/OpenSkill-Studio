from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_cors_policy_v9 import fleet_api_cors_policy_v9
def test_acp_v9():
    r = fleet_api_cors_policy_v9([{"strict": True, "allowed_origins": 5, "preflight_today": 1000}])
    assert r["strict"] == 1
    assert r["healthy"]
