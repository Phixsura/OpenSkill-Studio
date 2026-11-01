from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_comp import fleet_ai_model_compliance
def test_mc():
    r = fleet_ai_model_compliance([{"active": True, "models": 200, "passed": 200, "failed": 0, "frameworks": 10}])
    assert r["passed"] == 200
    assert r["compliant"]
