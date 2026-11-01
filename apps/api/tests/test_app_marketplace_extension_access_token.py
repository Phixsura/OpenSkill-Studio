from app.services.app_marketplace_extension_access_token import (
    AccessTokenService,
)
import pytest


def test_issue_and_validate():
    svc = AccessTokenService()
    result = svc.issue("ext-1", "user-1", ["read:data", "write:data"])
    assert result["access_token"].startswith("ext_")
    assert result["refresh_token"].startswith("ref_")
    v = svc.validate(result["access_token"])
    assert v["valid"] is True
    assert "read:data" in v["scopes"]


def test_invalid_scope():
    svc = AccessTokenService()
    with pytest.raises(ValueError, match="Invalid scope"):
        svc.issue("ext-1", "user-1", ["delete:everything"])


def test_check_scope():
    svc = AccessTokenService()
    result = svc.issue("ext-1", "user-1", ["read:data"])
    assert svc.check_scope(result["access_token"], "read:data") is True
    assert svc.check_scope(result["access_token"], "write:data") is False


def test_revoke():
    svc = AccessTokenService()
    result = svc.issue("ext-1", "user-1", ["read:data"])
    assert svc.revoke(result["token_id"]) is True
    v = svc.validate(result["access_token"])
    assert v["valid"] is False
    assert "revoked" in v["reason"].lower()


def test_expired_token():
    svc = AccessTokenService()
    result = svc.issue("ext-1", "user-1", ["read:data"], ttl=-1)
    v = svc.validate(result["access_token"])
    assert v["valid"] is False
    assert "expired" in v["reason"].lower()


def test_revoke_all():
    svc = AccessTokenService()
    svc.issue("ext-1", "u1", ["read:data"])
    svc.issue("ext-1", "u2", ["write:data"])
    svc.issue("ext-2", "u3", ["read:data"])
    count = svc.revoke_all("ext-1")
    assert count == 2


def test_token_not_found():
    svc = AccessTokenService()
    v = svc.validate("fake_token")
    assert v["valid"] is False
