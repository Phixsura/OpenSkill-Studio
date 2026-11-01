from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_security_v8 import fleet_ai_security_v8
def test_sv8():
    r = fleet_ai_security_v8([{"active": True, "score": 99, "threats_blocked": 100000, "zt": True, "encrypted_pct": 100}])
    assert r["hardened"]
