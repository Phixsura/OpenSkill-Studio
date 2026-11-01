"""Tests for App Team Member — add, roles, hierarchy, remove."""

import pytest

from app.services.app_team_member import AppTeamMember


class TestAddMember:
    def test_add(self):
        t = AppTeamMember()
        m = t.add_member("inst-1", "u1", "alice@x.com", role="admin", display_name="Alice")
        assert m.role == "admin"
        assert m.display_name == "Alice"

    def test_invalid_role(self):
        t = AppTeamMember()
        with pytest.raises(ValueError, match="Invalid role"):
            t.add_member("inst-1", "u1", "a@b.com", role="superadmin")

    def test_duplicate(self):
        t = AppTeamMember()
        t.add_member("inst-1", "u1", "a@b.com")
        with pytest.raises(ValueError, match="already exists"):
            t.add_member("inst-1", "u1", "a@b.com")


class TestUpdateRole:
    def test_update(self):
        t = AppTeamMember()
        t.add_member("inst-1", "u1", "a@b.com", role="member")
        m = t.update_role("inst-1", "u1", "admin")
        assert m.role == "admin"


class TestRoleHierarchy:
    def test_admin_has_member(self):
        t = AppTeamMember()
        t.add_member("inst-1", "u1", "a@b.com", role="admin")
        assert t.has_role_or_higher("inst-1", "u1", "member") is True

    def test_viewer_not_admin(self):
        t = AppTeamMember()
        t.add_member("inst-1", "u1", "a@b.com", role="viewer")
        assert t.has_role_or_higher("inst-1", "u1", "admin") is False

    def test_unknown_user(self):
        t = AppTeamMember()
        assert t.has_role_or_higher("inst-1", "nope", "viewer") is False


class TestRemove:
    def test_remove(self):
        t = AppTeamMember()
        t.add_member("inst-1", "u1", "a@b.com")
        assert t.remove_member("inst-1", "u1") is True
        assert t.member_count("inst-1") == 0


class TestList:
    def test_filter_role(self):
        t = AppTeamMember()
        t.add_member("inst-1", "u1", "a@b.com", role="admin")
        t.add_member("inst-1", "u2", "b@c.com", role="member")
        assert len(t.list_members("inst-1", role="admin")) == 1


class TestIsolation:
    def test_cross_installation(self):
        t = AppTeamMember()
        t.add_member("inst-1", "u1", "a@b.com")
        assert t.member_count("inst-2") == 0
