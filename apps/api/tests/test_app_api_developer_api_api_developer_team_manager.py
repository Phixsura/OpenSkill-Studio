import pytest
from app.services.app_api_developer_api_api_developer_team_manager import AppAPIDeveloperAPIApiDeveloperTeamManager

class TestTeamManager:
    def test_create_team(self):
        m = AppAPIDeveloperAPIApiDeveloperTeamManager()
        t = m.create_team("inst-1", "t1", "API Team", "owner1")
        assert t.member_count == 1
        assert t.members[0].role == "owner"

    def test_add_member(self):
        m = AppAPIDeveloperAPIApiDeveloperTeamManager()
        m.create_team("inst-1", "t1", "Team", "o1")
        t = m.add_member("inst-1", "t1", "d1", "developer")
        assert t.member_count == 2

    def test_duplicate_member(self):
        m = AppAPIDeveloperAPIApiDeveloperTeamManager()
        m.create_team("inst-1", "t1", "Team", "o1")
        with pytest.raises(ValueError, match="Already"):
            m.add_member("inst-1", "t1", "o1", "admin")

    def test_remove_member(self):
        m = AppAPIDeveloperAPIApiDeveloperTeamManager()
        m.create_team("inst-1", "t1", "Team", "o1")
        m.add_member("inst-1", "t1", "d1", "developer")
        t = m.remove_member("inst-1", "t1", "d1")
        assert t.member_count == 1

    def test_cannot_remove_owner(self):
        m = AppAPIDeveloperAPIApiDeveloperTeamManager()
        m.create_team("inst-1", "t1", "Team", "o1")
        with pytest.raises(ValueError, match="owner"):
            m.remove_member("inst-1", "t1", "o1")

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperTeamManager()
        m.create_team("inst-1", "t1", "Team", "o1")
        assert len(m.list_teams("inst-2")) == 0
