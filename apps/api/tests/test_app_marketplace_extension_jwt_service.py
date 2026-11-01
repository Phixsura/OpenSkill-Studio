from app.services.app_marketplace_extension_jwt_service import JwtTokenService, JwtError
import pytest
import time


def test_create_and_validate():
    svc = JwtTokenService(secret="test-secret")
    token = svc.create("user-123", audience="marketplace")
    claims = svc.validate(token, audience="marketplace")
    assert claims["sub"] == "user-123"
    assert claims["iss"] == "openskill-marketplace"
    assert claims["aud"] == "marketplace"


def test_expired_token():
    svc = JwtTokenService(secret="test-secret")
    token = svc.create("user-1", expires_in=-1)  # already expired
    with pytest.raises(JwtError, match="expired"):
        svc.validate(token)


def test_tampered_token():
    svc = JwtTokenService(secret="test-secret")
    token = svc.create("user-1")
    # Tamper with payload
    parts = token.split(".")
    tampered = parts[0] + "." + parts[1] + "x" + "." + parts[2]
    with pytest.raises(JwtError):
        svc.validate(tampered)


def test_wrong_secret():
    svc1 = JwtTokenService(secret="secret-1")
    svc2 = JwtTokenService(secret="secret-2")
    token = svc1.create("user-1")
    with pytest.raises(JwtError, match="Invalid signature"):
        svc2.validate(token)


def test_wrong_audience():
    svc = JwtTokenService(secret="test")
    token = svc.create("user-1", audience="app-a")
    with pytest.raises(JwtError, match="Invalid audience"):
        svc.validate(token, audience="app-b")


def test_custom_claims():
    svc = JwtTokenService(secret="test")
    token = svc.create("user-1", custom_claims={"role": "admin", "org": "acme"})
    claims = svc.validate(token)
    assert claims["role"] == "admin"
    assert claims["org"] == "acme"


def test_custom_claims_cant_override_standard():
    svc = JwtTokenService(secret="test")
    token = svc.create("user-1", custom_claims={"sub": "hacked"})
    claims = svc.validate(token)
    assert claims["sub"] == "user-1"  # not overridden


def test_revocation():
    svc = JwtTokenService(secret="test")
    token = svc.create("user-1")
    svc.validate(token)  # works
    svc.revoke(token)
    with pytest.raises(JwtError, match="revoked"):
        svc.validate(token)


def test_refresh_token_rotation():
    svc = JwtTokenService(secret="test")
    pair = svc.create_refresh_token("user-1")
    assert "access_token" in pair
    assert "refresh_token" in pair

    # Refresh
    new_pair = svc.refresh(pair["refresh_token"])
    assert new_pair is not None
    assert new_pair["access_token"] != pair["access_token"]

    # Old refresh token reuse → rejected (rotation)
    assert svc.refresh(pair["refresh_token"]) is None


def test_refresh_expired():
    svc = JwtTokenService(secret="test")
    pair = svc.create_refresh_token("user-1", refresh_ttl=0)
    time.sleep(0.01)
    assert svc.refresh(pair["refresh_token"]) is None
