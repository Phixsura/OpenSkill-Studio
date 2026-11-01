from app.services.app_marketplace_extension_sandbox_permissions import (
    SandboxPermissionService, Permission, GrantStatus,
)
import pytest


def test_declare_permissions():
    svc = SandboxPermissionService()
    result = svc.declare("ext-1", [Permission.FILE_READ, Permission.EXEC_SUBPROCESS])
    assert len(result["declared"]) == 2
    assert "exec:subprocess" in result["dangerous"]
    assert result["requires_review"] is True


def test_request_and_approve():
    svc = SandboxPermissionService()
    svc.declare("ext-1", [Permission.FILE_READ])
    grant = svc.request_grant("ext-1", "user-1", Permission.FILE_READ)
    assert grant.status == GrantStatus.PENDING
    svc.approve(grant.grant_id, "user-1")
    assert svc.check("ext-1", "user-1", Permission.FILE_READ) is True


def test_deny_permission():
    svc = SandboxPermissionService()
    svc.declare("ext-1", [Permission.CAMERA])
    grant = svc.request_grant("ext-1", "user-1", Permission.CAMERA)
    svc.deny(grant.grant_id, "Privacy concern", denier_user_id="user-1")
    assert svc.check("ext-1", "user-1", Permission.CAMERA) is False


def test_revoke_permission():
    svc = SandboxPermissionService()
    svc.declare("ext-1", [Permission.NETWORK_OUTBOUND])
    grant = svc.request_grant("ext-1", "user-1", Permission.NETWORK_OUTBOUND)
    svc.approve(grant.grant_id, "user-1")
    assert svc.check("ext-1", "user-1", Permission.NETWORK_OUTBOUND) is True
    svc.revoke(grant.grant_id)
    assert svc.check("ext-1", "user-1", Permission.NETWORK_OUTBOUND) is False


def test_undeclared_permission_rejected():
    svc = SandboxPermissionService()
    svc.declare("ext-1", [Permission.FILE_READ])
    with pytest.raises(ValueError, match="not declared"):
        svc.request_grant("ext-1", "user-1", Permission.EXEC_SUBPROCESS)


def test_idempotent_request():
    svc = SandboxPermissionService()
    svc.declare("ext-1", [Permission.STORAGE_LOCAL])
    g1 = svc.request_grant("ext-1", "user-1", Permission.STORAGE_LOCAL)
    g2 = svc.request_grant("ext-1", "user-1", Permission.STORAGE_LOCAL)
    assert g1.grant_id == g2.grant_id


def test_summary():
    svc = SandboxPermissionService()
    svc.declare("ext-1", [Permission.FILE_READ, Permission.FILE_WRITE])
    g1 = svc.request_grant("ext-1", "u1", Permission.FILE_READ)
    g2 = svc.request_grant("ext-1", "u1", Permission.FILE_WRITE)
    svc.approve(g1.grant_id, "u1")
    svc.deny(g2.grant_id, denier_user_id="u1")
    s = svc.get_summary("ext-1")
    assert s["granted"] == 1
    assert s["denied"] == 1


def test_wrong_user_cannot_approve():
    svc = SandboxPermissionService()
    svc.declare("ext-1", [Permission.FILE_READ])
    grant = svc.request_grant("ext-1", "user-1", Permission.FILE_READ)
    with pytest.raises(PermissionError, match="target user"):
        svc.approve(grant.grant_id, approver_user_id="attacker")
