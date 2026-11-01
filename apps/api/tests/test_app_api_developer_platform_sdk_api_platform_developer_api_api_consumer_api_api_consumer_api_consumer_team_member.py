import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_team_member import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember, TeamMember,
)

class TestConsumerTeamMember:
    def test_add_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember()
        svc.add_member("inst-1", TeamMember(member_id="m1", consumer_id="c1", email="a@b.com", role="owner"))
        svc.add_member("inst-1", TeamMember(member_id="m2", consumer_id="c1", email="b@b.com", role="member"))
        members = svc.list_members("inst-1", "c1")
        assert len(members) == 2 and members[0].role == "owner"

    def test_update_role(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember()
        svc.add_member("inst-1", TeamMember(member_id="m1", consumer_id="c1", email="a@b.com", role="admin"))
        svc.add_member("inst-1", TeamMember(member_id="m2", consumer_id="c1", email="b@b.com", role="viewer"))
        svc.update_role("inst-1", "c1", "m2", "member", by_member_id="m1")
        assert svc.get_member("inst-1", "c1", "m2").role == "member"

    def test_cannot_escalate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember()
        svc.add_member("inst-1", TeamMember(member_id="m1", consumer_id="c1", email="a@b.com", role="member"))
        svc.add_member("inst-1", TeamMember(member_id="m2", consumer_id="c1", email="b@b.com", role="viewer"))
        with pytest.raises(ValueError, match="Cannot assign role higher"):
            svc.update_role("inst-1", "c1", "m2", "admin", by_member_id="m1")

    def test_cannot_remove_last_owner(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember()
        svc.add_member("inst-1", TeamMember(member_id="m1", consumer_id="c1", email="a@b.com", role="owner"))
        with pytest.raises(ValueError, match="last owner"):
            svc.remove_member("inst-1", "c1", "m1")

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember()
        svc.add_member("inst-1", TeamMember(member_id="m1", consumer_id="c1", email="a@b.com"))
        with pytest.raises(ValueError, match="already exists"):
            svc.add_member("inst-1", TeamMember(member_id="m1", consumer_id="c1", email="a@b.com"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMember()
        svc.add_member("inst-1", TeamMember(member_id="m1", consumer_id="c1", email="a@b.com"))
        assert len(svc.list_members("inst-2", "c1")) == 0
