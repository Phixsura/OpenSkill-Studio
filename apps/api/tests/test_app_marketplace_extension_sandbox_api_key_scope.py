from app.services.app_marketplace_extension_sandbox_api_key_scope import (
    SandboxApiKeyScopeService,
)
import pytest


def test_create_and_validate():
    svc = SandboxApiKeyScopeService()
    result = svc.create_key("sb-1", "test-key", ["read:data", "read:config"])
    v = svc.validate(result["api_key"], "read:data")
    assert v["valid"] is True


def test_missing_scope():
    svc = SandboxApiKeyScopeService()
    result = svc.create_key("sb-1", "limited", ["read:data"])
    v = svc.validate(result["api_key"], "write:data")
    assert v["valid"] is False
    assert "Missing scope" in v["reason"]


def test_invalid_scope_rejected():
    svc = SandboxApiKeyScopeService()
    with pytest.raises(ValueError, match="Invalid scope"):
        svc.create_key("sb-1", "bad", ["delete:everything"])


def test_revoke():
    svc = SandboxApiKeyScopeService()
    result = svc.create_key("sb-1", "temp", ["read:data"])
    svc.revoke(result["key_id"])
    v = svc.validate(result["api_key"], "read:data")
    assert v["valid"] is False
    assert "revoked" in v["reason"]


def test_ip_restriction():
    svc = SandboxApiKeyScopeService()
    result = svc.create_key("sb-1", "ip-locked", ["read:data"],
                            ip_allowlist=["10.0.0.1"])
    v1 = svc.validate(result["api_key"], "read:data", client_ip="10.0.0.1")
    assert v1["valid"] is True
    v2 = svc.validate(result["api_key"], "read:data", client_ip="10.0.0.2")
    assert v2["valid"] is False


def test_usage_limit():
    svc = SandboxApiKeyScopeService()
    result = svc.create_key("sb-1", "limited", ["read:data"], max_usage=2)
    svc.validate(result["api_key"], "read:data")
    svc.validate(result["api_key"], "read:data")
    v = svc.validate(result["api_key"], "read:data")
    assert v["valid"] is False
    assert "Usage limit" in v["reason"]


def test_expiry():
    svc = SandboxApiKeyScopeService()
    result = svc.create_key("sb-1", "expired", ["read:data"], expires_in=-1)
    v = svc.validate(result["api_key"], "read:data")
    assert v["valid"] is False
    assert "expired" in v["reason"]


def test_list_keys():
    svc = SandboxApiKeyScopeService()
    svc.create_key("sb-1", "key-a", ["read:data"])
    svc.create_key("sb-1", "key-b", ["write:data"])
    svc.create_key("sb-2", "key-c", ["read:logs"])
    keys = svc.list_keys("sb-1")
    assert len(keys) == 2
