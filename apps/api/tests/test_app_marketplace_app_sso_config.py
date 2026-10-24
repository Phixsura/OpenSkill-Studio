from app.services.app_marketplace_app_sso_config import configure_sso, list_sso_providers

def test_configure_oidc():
    r = configure_sso(app_id="a1", provider="oidc", config={
        "issuer_url": "https://auth.example.com", "client_id": "cid", "client_secret": "secret"})
    assert r["status"] == "configured"
    assert "login_url" in r

def test_missing_fields():
    r = configure_sso(app_id="a1", provider="oidc", config={"issuer_url": "https://x.com"})
    assert "error" in r
    assert "client_id" in r["error"]

def test_invalid_url():
    r = configure_sso(app_id="a1", provider="oidc", config={
        "issuer_url": "not-a-url", "client_id": "x", "client_secret": "x"})
    assert "error" in r

def test_list():
    r = list_sso_providers()
    assert len(r["providers"]) == 3
