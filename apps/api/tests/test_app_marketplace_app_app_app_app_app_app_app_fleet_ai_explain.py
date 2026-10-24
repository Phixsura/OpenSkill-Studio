from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_explain import fleet_ai_explainability
def test_xai():
    r = fleet_ai_explainability([{"active": True, "explanations_24h": 100000, "methods": ["SHAP", "LIME", "attention"], "coverage": 92}])
    assert r["transparent"]
    assert "SHAP" in r["methods"]
