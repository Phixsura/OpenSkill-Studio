from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_sec_v4 import fleet_ai_security_v4
def test_sv4():
    r = fleet_ai_security_v4([{"active": True, "score": 98, "threats": 500, "zero_trust": True, "encrypted_pct": 100}])
    assert r["zero_trust"]
    assert r["hardened"]
