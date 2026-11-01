from app.services.app_marketplace_app_token_manager import issue_token, refresh_token, revoke_token

def test_issue():
    r = issue_token(client_id="c1", scopes=["read", "write"], expires_in_sec=7200)
    assert len(r["access_token"]) > 20
    assert r["token_type"] == "Bearer"
    assert r["expires_in"] == 7200
    assert r["scopes"] == ["read", "write"]

def test_refresh():
    r = refresh_token(refresh_tok=("x" * 30), client_id="c1")
    assert "access_token" in r

def test_refresh_invalid():
    r = refresh_token(refresh_tok="short", client_id="c1")
    assert "error" in r

def test_revoke():
    r = revoke_token(token_hash="abc123")
    assert r["revoked"]
