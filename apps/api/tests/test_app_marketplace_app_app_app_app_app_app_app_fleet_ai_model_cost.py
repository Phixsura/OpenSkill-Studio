from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_cost import fleet_ai_model_cost
def test_mc():
    r = fleet_ai_model_cost([{"active": True, "models": 100, "cost_usd": 50000, "cost_per_1k": 0.002}])
    assert r["cost_usd"] == 50000
    assert r["tracked"]
