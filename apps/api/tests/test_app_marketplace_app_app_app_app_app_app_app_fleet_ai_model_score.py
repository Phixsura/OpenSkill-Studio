from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_score import fleet_ai_model_scoring
def test_ms():
    r = fleet_ai_model_scoring([{"active": True, "models": 200, "avg_score": 92, "dimensions": 10}])
    assert r["avg_score"] == 92.0
    assert r["comprehensive"]
