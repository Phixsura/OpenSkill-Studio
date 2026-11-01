import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_reputation import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputation

class TestConsumerReputation:
    def test_default_trusted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputation()
        s = svc.get_or_create("inst-1", "c1")
        assert s.score == 100 and s.tier == "trusted"

    def test_penalize_to_restricted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputation()
        svc.penalize("inst-1", "c1", 60)
        s = svc.get_or_create("inst-1", "c1")
        assert s.score == 40 and s.tier == "restricted"

    def test_penalize_to_blocked(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputation()
        svc.penalize("inst-1", "c1", 90)
        assert len(svc.blocked_consumers("inst-1")) == 1

    def test_reward_recovery(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputation()
        svc.penalize("inst-1", "c1", 50)
        svc.reward("inst-1", "c1", 40)
        s = svc.get_or_create("inst-1", "c1")
        assert s.score == 90 and s.tier == "trusted"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerReputation()
        svc.get_or_create("inst-1", "c1")
        assert len(svc.list_scores("inst-2")) == 0
