from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_sig import fleet_ai_model_signature
def test_ms():
    r = fleet_ai_model_signature([{"active": True, "models": 200, "schemas": 400, "violations_24h": 0}])
    assert r["models"] == 200
    assert r["valid"]
