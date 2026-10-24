from app.services.app_marketplace_app_app_app_app_app_app_app_access_token import AccessTokenManager

def test_issue_validate():
    atm = AccessTokenManager(ttl_seconds=60)
    r = atm.issue("user-1", ["read", "write"])
    token = r["token"]
    v = atm.validate(token)
    assert v["valid"]
    assert v["subject"] == "user-1"
    assert "read" in v["scopes"]

def test_revoke():
    atm = AccessTokenManager()
    r = atm.issue("user-1", ["read"])
    atm.revoke(r["token"])
    v = atm.validate(r["token"])
    assert not v["valid"]
    assert v["reason"] == "revoked"

def test_expired():
    atm = AccessTokenManager(ttl_seconds=10)
    r = atm.issue("user-1", [])
    import time
    v = atm.validate(r["token"], now=time.time() + 11)
    assert not v["valid"]
    assert v["reason"] == "expired"
