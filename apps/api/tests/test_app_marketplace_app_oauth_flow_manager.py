from app.services.app_marketplace_app_oauth_flow_manager import generate_authorization_url, exchange_code_for_token, refresh_access_token, revoke_token

def test_auth_url():
    r = generate_authorization_url(client_id="c1", redirect_uri="https://app.com/callback", scopes=["read", "write"])
    assert "client_id=c1" in r["url"]
    assert len(r["state"]) > 20

def test_exchange():
    r = exchange_code_for_token(code="auth_code", client_id="c1", client_secret="secret")
    assert "access_token" in r
    assert r["token_type"] == "Bearer"

def test_refresh():
    r = refresh_access_token(refresh_token="old_refresh", client_id="c1")
    assert len(r["access_token"]) > 20

def test_revoke():
    r = revoke_token(token="some_token")
    assert r["revoked"]
