from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_identity_v8 import fleet_ai_identity_v8
def test_iv8():
    r = fleet_ai_identity_v8([{"active": True, "users": 10000000, "auth_24h": 500000000, "mfa_pct": 99, "zt": True}])
    assert r["users"] == 10000000
    assert r["secure"]
