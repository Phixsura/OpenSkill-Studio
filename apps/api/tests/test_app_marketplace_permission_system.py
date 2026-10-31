from app.services.app_marketplace_permission_system import (
    PermissionGrant, AVAILABLE_PERMISSIONS,
)


def test_grant_and_check():
    pg = PermissionGrant()
    granted = pg.grant("org-1", "ext-1", ["projects.read", "users.read"])
    assert len(granted) == 2
    assert pg.check("org-1", "ext-1", "projects.read") is True
    assert pg.check("org-1", "ext-1", "settings.admin") is False


def test_invalid_permissions_filtered():
    pg = PermissionGrant()
    granted = pg.grant("org-2", "ext-2", ["projects.read", "invalid.perm"])
    assert granted == ["projects.read"]


def test_revoke_specific():
    pg = PermissionGrant()
    pg.grant("org-3", "ext-3", ["projects.read", "users.read", "analytics.read"])
    pg.revoke("org-3", "ext-3", ["users.read"])
    assert pg.check("org-3", "ext-3", "users.read") is False
    assert pg.check("org-3", "ext-3", "projects.read") is True


def test_revoke_all():
    pg = PermissionGrant()
    pg.grant("org-4", "ext-4", ["projects.read", "users.read"])
    pg.revoke_all("org-4", "ext-4")
    assert pg.list_granted("org-4", "ext-4") == []


def test_list_granted():
    pg = PermissionGrant()
    pg.grant("org-5", "ext-5", ["submissions.write", "analytics.read"])
    granted = pg.list_granted("org-5", "ext-5")
    assert granted == ["analytics.read", "submissions.write"]


def test_audit():
    pg = PermissionGrant()
    pg.grant("org-6", "ext-a", ["projects.read"])
    pg.grant("org-6", "ext-b", ["users.read", "webhooks.manage"])
    audit = pg.audit("org-6")
    assert "ext-a" in audit
    assert "ext-b" in audit
    assert len(audit["ext-b"]) == 2


def test_available_permissions():
    assert len(AVAILABLE_PERMISSIONS) >= 8
    assert "projects.read" in AVAILABLE_PERMISSIONS
    assert "settings.admin" in AVAILABLE_PERMISSIONS
