import pytest
from app.services.app_marketplace_access_control import (
    AccessControl, Role, Action,
)


def test_viewer_permissions():
    ac = AccessControl()
    ac.assign_role("u1", "org-1", Role.VIEWER)
    assert ac.can("u1", "org-1", Action.VIEW_EXTENSION) is True
    assert ac.can("u1", "org-1", Action.INSTALL) is True
    assert ac.can("u1", "org-1", Action.CREATE_EXTENSION) is False
    assert ac.can("u1", "org-1", Action.MANAGE_USERS) is False


def test_developer_permissions():
    ac = AccessControl()
    ac.assign_role("u2", "org-1", Role.DEVELOPER)
    assert ac.can("u2", "org-1", Action.CREATE_EXTENSION) is True
    assert ac.can("u2", "org-1", Action.PUBLISH_EXTENSION) is True
    assert ac.can("u2", "org-1", Action.APPROVE_EXTENSION) is False


def test_admin_has_all():
    ac = AccessControl()
    ac.assign_role("u3", "org-1", Role.ADMIN)
    for action in Action:
        assert ac.can("u3", "org-1", action) is True


def test_no_role_denied():
    ac = AccessControl()
    assert ac.can("nobody", "org-1", Action.VIEW_EXTENSION) is False


def test_override():
    ac = AccessControl()
    ac.assign_role("u4", "org-1", Role.VIEWER)
    assert ac.can("u4", "org-1", Action.APPROVE_EXTENSION) is False
    ac.grant_override("u4", Action.APPROVE_EXTENSION)
    assert ac.can("u4", "org-1", Action.APPROVE_EXTENSION) is True
    ac.revoke_override("u4", Action.APPROVE_EXTENSION)
    assert ac.can("u4", "org-1", Action.APPROVE_EXTENSION) is False


def test_require_raises():
    ac = AccessControl()
    ac.assign_role("u5", "org-1", Role.VIEWER)
    with pytest.raises(PermissionError, match="lacks"):
        ac.require("u5", "org-1", Action.MANAGE_USERS)


def test_get_permissions():
    ac = AccessControl()
    ac.assign_role("u6", "org-1", Role.REVIEWER)
    perms = ac.get_permissions("u6", "org-1")
    assert "review.moderate" in perms
    assert "admin.approve" in perms
    assert "extension.create" not in perms
