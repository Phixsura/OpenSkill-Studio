from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_deploy_v8 import fleet_ai_deploy_v8
def test_dv8():
    r = fleet_ai_deploy_v8([{"active": True, "deploys_24h": 5000, "lead_min": 2, "zero_dt": True}])
    assert r["deploys"] == 5000
    assert r["instant"]
