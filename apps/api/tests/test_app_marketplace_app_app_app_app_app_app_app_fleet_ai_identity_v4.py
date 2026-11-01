from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_identity_v4 import fleet_ai_identity_v4
def test_iv4():
    r = fleet_ai_identity_v4([{"active": True, "users": 1000000, "auth_24h": 50000000, "mfa_pct": 98, "zero_trust": True}])
    assert r["users"] == 1000000
    assert r["secure"]
