"""Tests for Consumer Team Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_team_manager import TeamManager


class TestTeamManager:
    def test_create_team(self):
        svc = TeamManager()
        result = svc.create_team("t1", "Backend Team", "c1", "alice")
        assert result["owner"] == "alice"

    def test_add_member(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        result = svc.add_member("t1", "bob", "developer")
        assert result["member_count"] == 2

    def test_remove_member(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        svc.add_member("t1", "bob")
        result = svc.remove_member("t1", "bob")
        assert result["removed"] is True

    def test_cannot_remove_last_owner(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        with pytest.raises(ValueError):
            svc.remove_member("t1", "alice")

    def test_change_role(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        svc.add_member("t1", "bob", "viewer")
        result = svc.change_role("t1", "bob", "admin")
        assert result["new_role"] == "admin"

    def test_check_permission_allowed(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        result = svc.check_permission("t1", "alice", "admin")
        assert result["allowed"] is True

    def test_check_permission_denied(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        svc.add_member("t1", "bob", "viewer")
        result = svc.check_permission("t1", "bob", "admin")
        assert result["allowed"] is False

    def test_check_non_member(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        result = svc.check_permission("t1", "stranger", "viewer")
        assert result["allowed"] is False

    def test_invalid_role(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        with pytest.raises(ValueError):
            svc.add_member("t1", "bob", "superadmin")

    def test_duplicate_member(self):
        svc = TeamManager()
        svc.create_team("t1", "Team", "c1", "alice")
        with pytest.raises(ValueError):
            svc.add_member("t1", "alice", "developer")

    def test_list_teams(self):
        svc = TeamManager()
        svc.create_team("t1", "A", "c1", "alice")
        svc.create_team("t2", "B", "c2", "bob")
        assert len(svc.list_teams(consumer_id="c1")) == 1

    def test_isolation(self):
        a, b = TeamManager(), TeamManager()
        a.create_team("t1", "X", "c1", "alice")
        assert b.get_team("t1") is None
