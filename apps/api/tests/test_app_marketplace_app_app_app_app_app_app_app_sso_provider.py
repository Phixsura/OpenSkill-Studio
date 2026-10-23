from app.services.app_marketplace_app_app_app_app_app_app_app_sso_provider import SsoProviderManager

def test_sso():
    mgr = SsoProviderManager()
    r = mgr.add_provider(provider_id="okta1", name="Acme Okta", protocol="saml",
                          metadata_url="https://acme.okta.com/metadata", domains=["acme.com"])
    assert r["status"] == "configured"
    mgr.verify("okta1")
    found = mgr.resolve_provider("alice@acme.com")
    assert found["found"]
    assert found["provider_id"] == "okta1"
    not_found = mgr.resolve_provider("bob@other.com")
    assert not not_found["found"]

def test_http_rejected():
    mgr = SsoProviderManager()
    r = mgr.add_provider(provider_id="bad", name="Bad", protocol="saml",
                          metadata_url="http://insecure.com/meta", domains=["test.com"])
    assert "error" in r
