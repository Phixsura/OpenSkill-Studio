from app.services.app_marketplace_app_app_app_app_app_app_app_sso_provider import create_provider, list_providers

def test_create():
    r = create_provider("Google", "oauth2", "client123",
                         "https://accounts.google.com/o/oauth2/auth")
    assert r["created"]
    assert r["protocol"] == "oauth2"

def test_reject_http():
    r = create_provider("Bad", "oauth2", "x", "http://insecure.com/auth")
    assert not r["created"]
    assert r["error"] == "authorize_url must use https"

def test_list():
    providers = [
        {"name": "Google", "protocol": "oauth2", "status": "active"},
        {"name": "Okta", "protocol": "saml", "status": "active"},
        {"name": "Old", "protocol": "oidc", "status": "disabled"},
    ]
    r = list_providers(providers)
    assert r["total"] == 3
    assert r["active"] == 2
    assert r["by_protocol"]["saml"] == 1
