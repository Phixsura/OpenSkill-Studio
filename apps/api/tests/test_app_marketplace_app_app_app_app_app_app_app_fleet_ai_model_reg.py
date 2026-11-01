from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_reg import fleet_ai_model_registry
def test_mr():
    r = fleet_ai_model_registry([{"active": True, "models": 50, "versions": 200, "deployed": 40}])
    assert r["models"] == 50
    assert r["coverage"] == 80.0
