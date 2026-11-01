from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_card import fleet_ai_model_card
def test_mc():
    r = fleet_ai_model_card([{"active": True, "models": 200, "completeness_pct": 95, "sections": 12}])
    assert r["models"] == 200
    assert r["transparent"]
