"""Tests for App JWT Claims — extraction, validation, checks."""

import base64
import json
import time

import pytest

from app.services.app_jwt_claims import AppJWTClaims


def _make_jwt(claims: dict) -> str:
    """Create a fake JWT with the given payload claims."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256"}).encode()).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=").decode()
    signature = "fake_signature"
    return f"{header}.{payload}.{signature}"


class TestExtract:
    def test_extract(self):
        j = AppJWTClaims()
        token = _make_jwt({"sub": "user-1", "name": "Alice"})
        claims = j.extract_claims(token)
        assert claims["sub"] == "user-1"

    def test_invalid_format(self):
        j = AppJWTClaims()
        with pytest.raises(ValueError, match="3 parts"):
            j.extract_claims("not.a.jwt.token.here")

    def test_invalid_two_parts(self):
        j = AppJWTClaims()
        with pytest.raises(ValueError, match="3 parts"):
            j.extract_claims("only.two")


class TestValidate:
    def test_valid(self):
        j = AppJWTClaims()
        token = _make_jwt({"sub": "user-1"})
        r = j.validate(token)
        assert r.valid is True

    def test_required_claim_missing(self):
        j = AppJWTClaims(required_claims=["email"])
        token = _make_jwt({"sub": "user-1"})
        r = j.validate(token)
        assert r.valid is False
        assert any("email" in e for e in r.errors)

    def test_required_claim_present(self):
        j = AppJWTClaims(required_claims=["sub"])
        token = _make_jwt({"sub": "user-1"})
        r = j.validate(token)
        assert r.valid is True


class TestIssuer:
    def test_valid_issuer(self):
        j = AppJWTClaims(expected_issuer="https://auth.example.com")
        token = _make_jwt({"iss": "https://auth.example.com"})
        r = j.validate(token)
        assert r.valid is True

    def test_wrong_issuer(self):
        j = AppJWTClaims(expected_issuer="https://auth.example.com")
        token = _make_jwt({"iss": "https://evil.com"})
        r = j.validate(token)
        assert r.valid is False


class TestAudience:
    def test_valid_audience(self):
        j = AppJWTClaims(expected_audience="my-app")
        token = _make_jwt({"aud": "my-app"})
        r = j.validate(token)
        assert r.valid is True

    def test_audience_array(self):
        j = AppJWTClaims(expected_audience="my-app")
        token = _make_jwt({"aud": ["my-app", "other"]})
        r = j.validate(token)
        assert r.valid is True

    def test_wrong_audience(self):
        j = AppJWTClaims(expected_audience="my-app")
        token = _make_jwt({"aud": "other-app"})
        r = j.validate(token)
        assert r.valid is False


class TestExpiry:
    def test_not_expired(self):
        j = AppJWTClaims()
        token = _make_jwt({"exp": time.time() + 3600})
        r = j.validate(token)
        assert r.valid is True

    def test_expired(self):
        j = AppJWTClaims()
        token = _make_jwt({"exp": 1000})
        r = j.validate(token, now=2000)
        assert r.valid is False
        assert any("expired" in e.lower() for e in r.errors)
