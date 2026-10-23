from app.services.app_marketplace_app_app_app_app_app_app_app_oauth2_client import OAuth2ClientManager

def test_oauth2():
    mgr = OAuth2ClientManager()
    c = mgr.register(name="MyApp", redirect_uris=["https://myapp.com/callback"],
                      scopes=["read", "write"])
    assert c["client_id"].startswith("osk_")
    v = mgr.validate(c["client_id"], c["client_secret"])
    assert v["valid"]
    assert v["scopes"] == ["read", "write"]
    mgr.revoke(c["client_id"])
    v2 = mgr.validate(c["client_id"], c["client_secret"])
    assert not v2["valid"]
    assert v2["reason"] == "client_disabled"

def test_invalid_secret():
    mgr = OAuth2ClientManager()
    c = mgr.register(name="X", redirect_uris=["https://x.com/cb"], scopes=["read"])
    v = mgr.validate(c["client_id"], "wrong_secret")
    assert not v["valid"]
    assert v["reason"] == "invalid_secret"
