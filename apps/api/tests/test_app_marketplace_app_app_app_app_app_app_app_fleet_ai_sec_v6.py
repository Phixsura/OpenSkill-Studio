from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sec_v6 import fleet_ai_security_v6
def test_sv6():
    r = fleet_ai_security_v6([{"active": True, "score": 99, "threats_blocked": 10000, "zt": True}])
    assert r["hardened"]
