"""OAuth2 schema tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import OAuthAuthorizeRequest, OAuthTokenRequest, OAuthTokenResponse


def test_authorize_valid():
    r = OAuthAuthorizeRequest(client_id="abc", redirect_uri="https://app.com/cb", scope="read:cohorts", state="xyz")
    assert r.response_type == "code"

def test_authorize_missing_client_id():
    with pytest.raises(ValidationError):
        OAuthAuthorizeRequest(redirect_uri="https://x.com", scope="s", state="x")

def test_authorize_missing_state():
    with pytest.raises(ValidationError):
        OAuthAuthorizeRequest(client_id="c", redirect_uri="https://x.com", scope="s")

def test_token_request_auth_code():
    r = OAuthTokenRequest(grant_type="authorization_code", code="abc123", client_id="c", client_secret="s", redirect_uri="https://x.com")
    assert r.grant_type == "authorization_code"

def test_token_request_refresh():
    r = OAuthTokenRequest(grant_type="refresh_token", refresh_token="rt_abc", client_id="c", client_secret="s")
    assert r.refresh_token == "rt_abc"

def test_token_request_missing_secret():
    with pytest.raises(ValidationError):
        OAuthTokenRequest(grant_type="authorization_code", code="x", client_id="c")

def test_token_response():
    r = OAuthTokenResponse(access_token="at", refresh_token="rt", expires_in=3600, scope="read:cohorts")
    assert r.token_type == "bearer"
    assert r.expires_in == 3600

def test_token_response_missing_access_token():
    with pytest.raises(ValidationError):
        OAuthTokenResponse(refresh_token="rt", expires_in=3600, scope="s")
