from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sso import fleet_ai_sso
def test_sso():
    r = fleet_ai_sso([{"active": True, "logins_24h": 100000, "protocols": ["SAML", "OIDC"], "mfa_pct": 95}])
    assert r["logins_24h"] == 100000
    assert r["secure"]
