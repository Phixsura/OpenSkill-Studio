import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_group import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroup, ConsumerGroup,
)

class TestConsumerGroup:
    def test_create_and_add_member(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="Premium"))
        g = svc.add_member("inst-1", "g1", "c1")
        assert "c1" in g.members

    def test_duplicate_member(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="Test"))
        svc.add_member("inst-1", "g1", "c1")
        with pytest.raises(ValueError, match="already in"):
            svc.add_member("inst-1", "g1", "c1")

    def test_group_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="Small", max_members=2))
        svc.add_member("inst-1", "g1", "c1")
        svc.add_member("inst-1", "g1", "c2")
        with pytest.raises(ValueError, match="full"):
            svc.add_member("inst-1", "g1", "c3")

    def test_groups_for_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="A"))
        svc.create_group("inst-1", ConsumerGroup(group_id="g2", name="B"))
        svc.add_member("inst-1", "g1", "c1")
        svc.add_member("inst-1", "g2", "c1")
        groups = svc.groups_for_consumer("inst-1", "c1")
        assert len(groups) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="Test"))
        assert len(svc.list_groups("inst-2")) == 0
