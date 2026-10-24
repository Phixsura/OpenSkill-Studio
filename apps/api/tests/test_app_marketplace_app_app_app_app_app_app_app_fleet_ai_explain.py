from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_explain import fleet_ai_explainability
def test_exp():
    r = fleet_ai_explainability([{"active": True, "explanations_24h": 500000, "models": 30}])
    assert r["explanations_24h"] == 500000
    assert r["transparent"]
