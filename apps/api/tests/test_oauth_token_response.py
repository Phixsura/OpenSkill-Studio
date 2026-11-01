"""OAuth token response schema tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import OAuthTokenResponse

def test_valid_response():
    r = OAuthTokenResponse(access_token="at_abc", refresh_token="rt_xyz", expires_in=3600, scope="read:cohorts")
    assert r.token_type == "bearer"
    assert r.expires_in == 3600

def test_custom_expires():
    r = OAuthTokenResponse(access_token="at", refresh_token="rt", expires_in=7200, scope="read:cohorts write:projects")
    assert r.expires_in == 7200

def test_missing_access_token():
    with pytest.raises(ValidationError):
        OAuthTokenResponse(refresh_token="rt", expires_in=3600, scope="s")

def test_missing_refresh_token():
    with pytest.raises(ValidationError):
        OAuthTokenResponse(access_token="at", expires_in=3600, scope="s")

def test_missing_scope():
    with pytest.raises(ValidationError):
        OAuthTokenResponse(access_token="at", refresh_token="rt", expires_in=3600)

def test_serialization():
    r = OAuthTokenResponse(access_token="at", refresh_token="rt", expires_in=3600, scope="s")
    d = r.model_dump()
    assert d["token_type"] == "bearer"
    assert "access_token" in d
    assert "refresh_token" in d
