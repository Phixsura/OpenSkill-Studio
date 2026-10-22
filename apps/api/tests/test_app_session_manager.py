"""OAuth session manager tests."""
import pytest
from app.services.app_session_manager import create_auth_code, consume_auth_code, revoke_session

def test_create_code():
    code = create_auth_code(client_id="c1", redirect_uri="https://x.com/cb", scopes=["read:cohorts"], user_id="u1", state="s1")
    assert len(code) > 20

def test_consume_code():
    code = create_auth_code(client_id="c2", redirect_uri="https://x.com/cb", scopes=[], user_id="u1", state="s")
    result = consume_auth_code(code, client_id="c2", redirect_uri="https://x.com/cb")
    assert result is not None
    assert result["user_id"] == "u1"

def test_consume_only_once():
    code = create_auth_code(client_id="c3", redirect_uri="https://x.com/cb", scopes=[], user_id="u1", state="s")
    consume_auth_code(code, client_id="c3", redirect_uri="https://x.com/cb")
    assert consume_auth_code(code, client_id="c3", redirect_uri="https://x.com/cb") is None

def test_consume_wrong_client():
    code = create_auth_code(client_id="c4", redirect_uri="https://x.com/cb", scopes=[], user_id="u1", state="s")
    assert consume_auth_code(code, client_id="wrong", redirect_uri="https://x.com/cb") is None

def test_consume_wrong_redirect():
    code = create_auth_code(client_id="c5", redirect_uri="https://x.com/cb", scopes=[], user_id="u1", state="s")
    assert consume_auth_code(code, client_id="c5", redirect_uri="https://evil.com/cb") is None

def test_consume_unknown_code():
    assert consume_auth_code("nonexistent", client_id="c", redirect_uri="u") is None

def test_revoke_missing():
    assert revoke_session("nonexistent") is False
