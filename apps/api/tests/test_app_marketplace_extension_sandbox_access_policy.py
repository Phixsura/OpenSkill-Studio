from app.services.app_marketplace_extension_sandbox_access_policy import (
    SandboxAccessPolicyService, Action,
)
import pytest


def test_define_role_and_assign():
    svc = SandboxAccessPolicyService()
    svc.define_role("viewer", [{"resource": "files:*", "actions": ["read"]}])
    assert svc.assign_role("sb-1", "user-1", "viewer") is True


def test_check_allowed():
    svc = SandboxAccessPolicyService()
    svc.define_role("editor", [
        {"resource": "files:*", "actions": ["read", "write"]},
    ])
    svc.assign_role("sb-1", "user-1", "editor")
    result = svc.check_access("sb-1", "user-1", "files:src/index.ts", Action.WRITE)
    assert result["allowed"] is True


def test_check_denied_no_rule():
    svc = SandboxAccessPolicyService()
    svc.define_role("viewer", [{"resource": "files:*", "actions": ["read"]}])
    svc.assign_role("sb-1", "user-1", "viewer")
    result = svc.check_access("sb-1", "user-1", "files:src/index.ts", Action.DELETE)
    assert result["allowed"] is False


def test_explicit_deny():
    svc = SandboxAccessPolicyService()
    svc.define_role("restricted", [
        {"resource": "files:*", "actions": ["read", "write"]},
        {"resource": "files:secrets", "actions": ["read", "write"], "decision": "deny"},
    ])
    svc.assign_role("sb-1", "user-1", "restricted")
    assert svc.check_access("sb-1", "user-1", "files:secrets", Action.READ)["allowed"] is False
    assert svc.check_access("sb-1", "user-1", "files:src", Action.READ)["allowed"] is True


def test_role_inheritance():
    svc = SandboxAccessPolicyService()
    svc.define_role("viewer", [{"resource": "files:*", "actions": ["read"]}])
    svc.define_role("editor", [{"resource": "files:*", "actions": ["write"]}], inherits=["viewer"])
    svc.assign_role("sb-1", "user-1", "editor")
    # Should have both read (inherited) and write
    assert svc.check_access("sb-1", "user-1", "files:x", Action.READ)["allowed"] is True
    assert svc.check_access("sb-1", "user-1", "files:x", Action.WRITE)["allowed"] is True


def test_no_role_assigned():
    svc = SandboxAccessPolicyService()
    result = svc.check_access("sb-1", "unknown", "files:x", Action.READ)
    assert result["allowed"] is False
    assert "No role" in result["reason"]


def test_wildcard_resource():
    svc = SandboxAccessPolicyService()
    svc.define_role("admin", [{"resource": "*", "actions": ["read", "write", "delete", "admin"]}])
    svc.assign_role("sb-1", "admin-1", "admin")
    assert svc.check_access("sb-1", "admin-1", "anything", Action.ADMIN)["allowed"] is True


def test_invalid_parent():
    svc = SandboxAccessPolicyService()
    with pytest.raises(ValueError, match="not found"):
        svc.define_role("child", [], inherits=["nonexistent"])
