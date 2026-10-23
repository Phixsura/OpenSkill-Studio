from app.services.app_marketplace_app_app_app_app_app_app_app_access_token import (
    issue_token, validate_token, revoke_token, clear_tokens,
)

def test_issue_validate():
    clear_tokens()
    t = issue_token("user:123", ["read", "write"])
    assert len(t["token"]) > 20
    v = validate_token(t["token"])
    assert v["valid"]
    assert v["subject"] == "user:123"
    v2 = validate_token(t["token"], required_scope="admin")
    assert not v2["valid"]
    assert v2["error"] == "insufficient_scope"
    clear_tokens()

def test_revoke():
    clear_tokens()
    t = issue_token("u", ["read"])
    revoke_token(t["token"])
    v = validate_token(t["token"])
    assert not v["valid"]
    assert v["error"] == "revoked"
    clear_tokens()
