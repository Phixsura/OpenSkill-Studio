"""OAuth schema edge cases."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import OAuthAuthorizeRequest, OAuthTokenRequest

def test_authorize_custom_response_type():
    r = OAuthAuthorizeRequest(client_id="c", redirect_uri="https://x.com/cb", scope="read:cohorts", state="s", response_type="code")
    assert r.response_type == "code"

def test_token_grant_types():
    for gt in ["authorization_code", "refresh_token"]:
        r = OAuthTokenRequest(grant_type=gt, client_id="c", client_secret="s")
        assert r.grant_type == gt

def test_token_with_code():
    r = OAuthTokenRequest(grant_type="authorization_code", code="abc", client_id="c", client_secret="s", redirect_uri="https://x.com")
    assert r.code == "abc"

def test_token_with_refresh():
    r = OAuthTokenRequest(grant_type="refresh_token", refresh_token="rt", client_id="c", client_secret="s")
    assert r.refresh_token == "rt"

def test_authorize_long_state():
    state = "x" * 256
    r = OAuthAuthorizeRequest(client_id="c", redirect_uri="https://x.com", scope="s", state=state)
    assert len(r.state) == 256

def test_authorize_scope_multiple():
    r = OAuthAuthorizeRequest(client_id="c", redirect_uri="https://x.com", scope="read:cohorts write:projects", state="s")
    assert "read:cohorts" in r.scope
