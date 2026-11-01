from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_warm import fleet_ai_model_warmup
def test_mw():
    r = fleet_ai_model_warmup([{"active": True, "warmed": 50, "prevented": 500000, "warmup_s": 15}])
    assert r["warmed"] == 50
    assert r["ready"]
