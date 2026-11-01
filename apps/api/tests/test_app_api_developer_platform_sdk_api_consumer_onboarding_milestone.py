import pytest
from app.services.app_api_developer_platform_sdk_api_consumer_onboarding_milestone import AppAPIDeveloperPlatformSDKApiConsumerOnboardingMilestone

class TestConsumerOnboardingMilestone:
    def test_achieve(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerOnboardingMilestone()
        c = m.achieve("inst-1", "c1", "registered")
        assert c.completed_count == 1
        assert c.next_milestone == "api_key_created"

    def test_invalid_milestone(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerOnboardingMilestone()
        with pytest.raises(ValueError):
            m.achieve("inst-1", "c1", "unknown")

    def test_fully_onboarded(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerOnboardingMilestone()
        for ms in ["registered", "api_key_created", "first_api_call", "first_webhook", "production_traffic", "first_payment"]:
            m.achieve("inst-1", "c1", ms)
        c = m.get("inst-1", "c1")
        assert c.fully_onboarded is True
        assert c.completion_pct == 100.0

    def test_completion_rate(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerOnboardingMilestone()
        for ms in ["registered", "api_key_created", "first_api_call", "first_webhook", "production_traffic", "first_payment"]:
            m.achieve("inst-1", "c1", ms)
        m.achieve("inst-1", "c2", "registered")
        assert m.completion_rate("inst-1") == 50.0

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiConsumerOnboardingMilestone()
        m.achieve("inst-1", "c1", "registered")
        assert m.completion_rate("inst-2") == 0.0
