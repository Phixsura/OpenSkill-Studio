from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rl_v4 import fleet_ai_rate_limiter_v4
def test_rlv4():
    r = fleet_ai_rate_limiter_v4([{"active": True, "rules": 500, "throttled": 10000, "adaptive": True}])
    assert r["rules"] == 500
    assert r["smart"]
