from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_ab_cmp import fleet_ai_model_ab_compare
def test_abc():
    r = fleet_ai_model_ab_compare([{"active": True, "comparisons_24h": 100000, "winners": 80000, "ties": 20000}])
    assert r["comparisons_24h"] == 100000
    assert r["comparing"]
