from app.services.app_marketplace_app_app_app_app_app_app_app_access_token_mgr import AccessTokenManager

def test_token_lifecycle():
    mgr = AccessTokenManager()
    t = mgr.create_token(name="CI", scopes=["read", "write"], expires_in=3600)
    assert len(t["token"]) > 20
    v = mgr.validate_token(t["token"])
    assert v["valid"]
    assert v["scopes"] == ["read", "write"]
    r = mgr.revoke_token(t["token"])
    assert r["status"] == "revoked"
    v2 = mgr.validate_token(t["token"])
    assert not v2["valid"]
    assert v2["reason"] == "revoked"

def test_invalid():
    mgr = AccessTokenManager()
    v = mgr.validate_token("bogus")
    assert not v["valid"]
    assert v["reason"] == "not_found"
