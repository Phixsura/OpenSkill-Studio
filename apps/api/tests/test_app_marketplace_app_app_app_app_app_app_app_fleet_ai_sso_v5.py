from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sso_v5 import fleet_ai_sso_v5
def test_sv5():
    r = fleet_ai_sso_v5([{"active": True, "logins": 1000000, "protocols": ["SAML", "OIDC", "OAuth2"], "mfa": True}])
    assert r["logins_24h"] == 1000000
    assert r["enterprise"]
