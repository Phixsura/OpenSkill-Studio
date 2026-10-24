from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sandbox_env import fleet_ai_sandbox_env
def test_se():
    r = fleet_ai_sandbox_env([{"active": True, "environments": 200, "sessions_24h": 5000, "lifetime_h": 4}])
    assert r["environments"] == 200
    assert r["available"]
