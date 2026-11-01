from app.services.app_marketplace_extension_connector_oauth import ConnectorOAuthService

def test_initiate_and_complete():
    svc = ConnectorOAuthService()
    s = svc.initiate("slack", "u1", "https://app/callback", ["read", "write"])
    assert s.status == "pending"
    result = svc.complete(s.session_id, s.state)
    assert result is not None
    assert result.status == "authorized"
    assert result.access_token != ""

def test_bad_state():
    svc = ConnectorOAuthService()
    s = svc.initiate("slack", "u1", "https://app/callback", [])
    assert svc.complete(s.session_id, "wrong-state") is None

def test_get_token():
    svc = ConnectorOAuthService()
    s = svc.initiate("slack", "u1", "https://app/callback", [])
    svc.complete(s.session_id, s.state)
    assert svc.get_token("u1", "slack") is not None

def test_revoke():
    svc = ConnectorOAuthService()
    s = svc.initiate("slack", "u1", "https://app/callback", [])
    svc.complete(s.session_id, s.state)
    assert svc.revoke("u1", "slack") is True
    assert svc.get_token("u1", "slack") is None
