from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_cat import fleet_ai_model_catalog
def test_mc():
    r = fleet_ai_model_catalog([{"active": True, "models": 500, "providers": 20, "deployments": 200}])
    assert r["models"] == 500
    assert r["comprehensive"]
