from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_depr import fleet_ai_model_deprecation
def test_md():
    r = fleet_ai_model_deprecation([{"active": True, "deprecated": 20, "migrated": 18, "sunset_days": 30}])
    assert r["deprecated"] == 20
    assert r["planned"]
