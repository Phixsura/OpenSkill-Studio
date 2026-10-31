from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_deploy import fleet_ai_deploy
def test_dep():
    r = fleet_ai_deploy([{"active": True, "deployments_24h": 100, "rollbacks_24h": 0}])
    assert r["deployments_24h"] == 100
    assert r["reliable"]
