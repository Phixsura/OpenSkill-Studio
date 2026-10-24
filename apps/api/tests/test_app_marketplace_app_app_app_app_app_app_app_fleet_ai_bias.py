from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_bias import fleet_ai_bias
def test_bias():
    r = fleet_ai_bias([{"active": True, "models_audited": 50, "bias_alerts_24h": 0}])
    assert r["models_audited"] == 50
    assert r["fair"]
