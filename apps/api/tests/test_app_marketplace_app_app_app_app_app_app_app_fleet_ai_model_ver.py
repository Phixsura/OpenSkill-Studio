from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_ver import fleet_ai_model_versioner
def test_mv():
    r = fleet_ai_model_versioner([{"active": True, "models": 100, "versions": 1000, "rollbacks": 2}])
    assert r["versions"] == 1000
    assert r["stable"]
