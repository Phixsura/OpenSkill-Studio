from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_merge import fleet_ai_model_merge
def test_mm():
    r = fleet_ai_model_merge([{"active": True, "merges": 100, "methods": ["SLERP", "TIES", "DARE"], "improvement_pct": 12}])
    assert r["merges"] == 100
    assert r["effective"]
