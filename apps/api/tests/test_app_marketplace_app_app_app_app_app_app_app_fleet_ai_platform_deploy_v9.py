from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_deploy_v9 import fleet_ai_deploy_v9
def test_dv9():
    r = fleet_ai_deploy_v9([{"active": True, "deploys_24h": 10000, "lead_min": 1, "zero_dt": True}])
    assert r["deploys"] == 10000
    assert r["instant"]
