import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_api_changelog_subscription import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscription, ChangelogSubscription,
)

class TestChangelogSubscription:
    def test_subscribe_and_notify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscription()
        svc.subscribe("inst-1", ChangelogSubscription(consumer_id="c1", channels=["email", "webhook"]))
        count = svc.notify("inst-1", "feature")
        assert count == 1

    def test_category_filter(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscription()
        svc.subscribe("inst-1", ChangelogSubscription(consumer_id="c1", categories=["breaking", "security"]))
        assert svc.notify("inst-1", "feature") == 0
        assert svc.notify("inst-1", "breaking") == 1

    def test_unsubscribe(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscription()
        svc.subscribe("inst-1", ChangelogSubscription(consumer_id="c1"))
        svc.unsubscribe("inst-1", "c1")
        assert len(svc.active_subscribers("inst-1")) == 0

    def test_invalid_channel(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscription()
        with pytest.raises(ValueError, match="Invalid channels"):
            svc.subscribe("inst-1", ChangelogSubscription(consumer_id="c1", channels=["sms"]))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiApiChangelogSubscription()
        svc.subscribe("inst-1", ChangelogSubscription(consumer_id="c1"))
        assert len(svc.list_subs("inst-2")) == 0
