from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_sec_v2 import fleet_ai_model_security_v2
def test_msv2():
    r = fleet_ai_model_security_v2([{"active": True, "models": 500, "threats": 100, "encrypted_pct": 100}])
    assert r["models"] == 500
    assert r["secure"]
