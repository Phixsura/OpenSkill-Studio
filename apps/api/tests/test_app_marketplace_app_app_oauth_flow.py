from app.services.app_marketplace_app_app_oauth_flow import generate_auth_url, verify_state

def test_auth_url():
    r = generate_auth_url(client_id="app123", redirect_uri="https://myapp.com/callback",
                          scopes=["read", "write"])
    assert "url" in r
    assert "auth.openskill.dev" in r["url"]
    assert r["scopes"] == ["read", "write"]
    assert len(r["state"]) > 20

def test_state_verification():
    r = generate_auth_url(client_id="x", redirect_uri="https://a.com/cb", scopes=["read"])
    assert verify_state(state=r["state"], signature=r["state_sig"])
    assert not verify_state(state=r["state"], signature="bad_sig_0000000")

def test_bad_redirect():
    r = generate_auth_url(client_id="x", redirect_uri="javascript:alert(1)", scopes=[])
    assert "error" in r
