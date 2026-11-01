from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_reg_v3 import fleet_ai_model_registry_v3
def test_mrv3():
    r = fleet_ai_model_registry_v3([{"active": True, "models": 1000, "versions": 10000, "deployments": 500, "tags": 5000}])
    assert r["models"] == 1000
    assert r["comprehensive"]
