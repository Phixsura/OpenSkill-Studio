"""Tests for App Permission Policy — roles, assignment, authorization."""

import pytest

from app.services.app_permission_policy import AppPermissionPolicy

ADMIN_PERMS = [{"resource": "app", "action": "admin"}]
VIEWER_PERMS = [{"resource": "app", "action": "read"}, {"resource": "webhook", "action": "read"}]


class TestRole:
    def test_create(self):
        p = AppPermissionPolicy()
        r = p.create_role("inst-1", "admin", "Admin", ADMIN_PERMS)
        assert len(r.permissions) == 1

    def test_admin_grants_all(self):
        p = AppPermissionPolicy()
        p.create_role("inst-1", "admin", "Admin", ADMIN_PERMS)
        p.assign_role("inst-1", "alice", "admin")
        assert p.check("inst-1", "alice", "app", "read") is True
        assert p.check("inst-1", "alice", "app", "write") is True


class TestAssign:
    def test_assign_and_check(self):
        p = AppPermissionPolicy()
        p.create_role("inst-1", "viewer", "Viewer", VIEWER_PERMS)
        p.assign_role("inst-1", "bob", "viewer")
        assert p.check("inst-1", "bob", "app", "read") is True
        assert p.check("inst-1", "bob", "app", "write") is False

    def test_no_role(self):
        p = AppPermissionPolicy()
        assert p.check("inst-1", "nobody", "app", "read") is False

    def test_invalid_role(self):
        p = AppPermissionPolicy()
        with pytest.raises(KeyError):
            p.assign_role("inst-1", "alice", "nonexistent")


class TestUserPermissions:
    def test_list(self):
        p = AppPermissionPolicy()
        p.create_role("inst-1", "viewer", "Viewer", VIEWER_PERMS)
        p.assign_role("inst-1", "bob", "viewer")
        perms = p.user_permissions("inst-1", "bob")
        assert "app:read" in perms
        assert "webhook:read" in perms


class TestIsolation:
    def test_cross(self):
        p = AppPermissionPolicy()
        p.create_role("inst-1", "admin", "Admin", ADMIN_PERMS)
        p.assign_role("inst-1", "alice", "admin")
        assert p.check("inst-2", "alice", "app", "read") is False
