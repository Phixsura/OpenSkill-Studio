import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_group import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup, ConsumerGroup,
)

class TestConsumerApiConsumerGroup:
    def test_create_and_add(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="Enterprise"))
        svc.add_member("inst-1", "g1", "c1")
        svc.add_member("inst-1", "g1", "c2")
        groups = svc.get_consumer_groups("inst-1", "c1")
        assert len(groups) == 1 and "c2" in groups[0].members

    def test_remove_member(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="G"))
        svc.add_member("inst-1", "g1", "c1")
        svc.remove_member("inst-1", "g1", "c1")
        assert len(svc.get_consumer_groups("inst-1", "c1")) == 0

    def test_set_policy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="G"))
        svc.set_policy("inst-1", "g1", "rate_limit", "rl-enterprise")
        group = svc.list_groups("inst-1")[0]
        assert group.policies["rate_limit"] == "rl-enterprise"

    def test_duplicate_member(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="G"))
        svc.add_member("inst-1", "g1", "c1")
        with pytest.raises(ValueError, match="already in group"):
            svc.add_member("inst-1", "g1", "c1")

    def test_duplicate_group(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="G"))
        with pytest.raises(ValueError, match="already exists"):
            svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="G2"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerGroup()
        svc.create_group("inst-1", ConsumerGroup(group_id="g1", name="G"))
        assert len(svc.list_groups("inst-2")) == 0
