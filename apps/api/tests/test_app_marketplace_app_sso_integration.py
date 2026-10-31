from app.services.app_marketplace_app_sso_integration import create_sso_config, generate_state_param, validate_callback, build_sso_metadata

def test_create():
    c = create_sso_config(app_id="a1", provider="oidc", client_id="c1",
                           issuer_url="https://auth.example.com", callback_url="https://app.com/callback")
    assert c["status"] == "configured"

def test_invalid_provider():
    c = create_sso_config(app_id="a1", provider="ldap", client_id="c1",
                           issuer_url="x", callback_url="y")
    assert c["error"]

def test_state():
    s = generate_state_param(session_id="sess1")
    assert len(s) == 32

def test_validate_ok():
    r = validate_callback(state="abc", code="xyz", expected_state="abc")
    assert r["valid"]

def test_validate_csrf():
    r = validate_callback(state="abc", code="xyz", expected_state="def")
    assert not r["valid"]
    assert "CSRF" in r["error"]

def test_metadata():
    m = build_sso_metadata(app={"slug": "my-app"}, sso_config={"callback_url": "https://x.com/cb", "provider": "oidc"})
    assert "my-app" in m["entity_id"]
