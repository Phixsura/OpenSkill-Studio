"""Tests for App Permission Matrix — roles, grants, wildcards, inheritance."""

import pytest

from app.services.app_permission_matrix import AppPermissionMatrix


class TestCreateRole:
    def test_create(self):
        m = AppPermissionMatrix()
        r = m.create_role("inst-1", "admin", "Administrator")
        assert r.role_id == "admin"
        assert r.name == "Administrator"

    def test_duplicate(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        with pytest.raises(ValueError, match="already exists"):
            m.create_role("inst-1", "admin", "Admin 2")

    def test_missing_name(self):
        m = AppPermissionMatrix()
        with pytest.raises(ValueError, match="name"):
            m.create_role("inst-1", "admin", "")

    def test_inheritance(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "viewer", "Viewer")
        r = m.create_role("inst-1", "editor", "Editor", inherits_from="viewer")
        assert r.inherits_from == "viewer"

    def test_invalid_parent(self):
        m = AppPermissionMatrix()
        with pytest.raises(KeyError, match="Parent role"):
            m.create_role("inst-1", "editor", "Editor", inherits_from="nope")


class TestGrantPermission:
    def test_grant(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        p = m.grant_permission("inst-1", "admin", "projects", "read")
        assert p.resource == "projects"
        assert p.action == "read"

    def test_duplicate_grant_idempotent(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        m.grant_permission("inst-1", "admin", "projects", "read")
        m.grant_permission("inst-1", "admin", "projects", "read")
        role = m.get_role("inst-1", "admin")
        assert len(role.permissions) == 1

    def test_missing_resource(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        with pytest.raises(ValueError, match="resource"):
            m.grant_permission("inst-1", "admin", "", "read")


class TestRevokePermission:
    def test_revoke(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        m.grant_permission("inst-1", "admin", "projects", "read")
        assert m.revoke_permission("inst-1", "admin", "projects", "read") is True
        role = m.get_role("inst-1", "admin")
        assert len(role.permissions) == 0

    def test_revoke_nonexistent(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        assert m.revoke_permission("inst-1", "admin", "x", "y") is False


class TestCheckPermission:
    def test_direct_match(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "editor", "Editor")
        m.grant_permission("inst-1", "editor", "projects", "write")
        result = m.check_permission("inst-1", "editor", "projects", "write")
        assert result.allowed is True
        assert result.reason == "direct"

    def test_denied(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "viewer", "Viewer")
        m.grant_permission("inst-1", "viewer", "projects", "read")
        result = m.check_permission("inst-1", "viewer", "projects", "delete")
        assert result.allowed is False
        assert result.reason == "denied"

    def test_wildcard(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        m.grant_permission("inst-1", "admin", "projects", "*")
        result = m.check_permission("inst-1", "admin", "projects", "delete")
        assert result.allowed is True
        assert result.reason == "wildcard"

    def test_inherited(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "viewer", "Viewer")
        m.grant_permission("inst-1", "viewer", "projects", "read")
        m.create_role("inst-1", "editor", "Editor", inherits_from="viewer")
        result = m.check_permission("inst-1", "editor", "projects", "read")
        assert result.allowed is True
        assert result.reason == "inherited"

    def test_unknown_role_denied(self):
        m = AppPermissionMatrix()
        result = m.check_permission("inst-1", "ghost", "x", "y")
        assert result.allowed is False


class TestEffectivePermissions:
    def test_includes_inherited(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "viewer", "Viewer")
        m.grant_permission("inst-1", "viewer", "projects", "read")
        m.create_role("inst-1", "editor", "Editor", inherits_from="viewer")
        m.grant_permission("inst-1", "editor", "projects", "write")
        perms = m.get_effective_permissions("inst-1", "editor")
        resources = {(p.resource, p.action) for p in perms}
        assert ("projects", "read") in resources
        assert ("projects", "write") in resources

    def test_no_duplicates(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "viewer", "Viewer")
        m.grant_permission("inst-1", "viewer", "projects", "read")
        m.create_role("inst-1", "editor", "Editor", inherits_from="viewer")
        m.grant_permission("inst-1", "editor", "projects", "read")  # duplicate
        perms = m.get_effective_permissions("inst-1", "editor")
        assert len(perms) == 1


class TestListRoles:
    def test_list(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        m.create_role("inst-1", "viewer", "Viewer")
        m.create_role("inst-2", "other", "Other")
        assert len(m.list_roles("inst-1")) == 2


class TestIsolation:
    def test_cross_installation(self):
        m = AppPermissionMatrix()
        m.create_role("inst-1", "admin", "Admin")
        with pytest.raises(KeyError):
            m.get_role("inst-2", "admin")
