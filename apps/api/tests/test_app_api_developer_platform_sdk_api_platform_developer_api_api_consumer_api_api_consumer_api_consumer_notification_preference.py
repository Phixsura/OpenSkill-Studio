import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_notification_preference import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreference, NotificationPreference, NotificationChannel,
)

class TestConsumerNotificationPreference:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreference()
        pref = NotificationPreference(consumer_id="c1", channels=[NotificationChannel(channel_type="email", target="a@b.com")], digest_mode="daily")
        svc.set_preference("inst-1", pref)
        got = svc.get_preference("inst-1", "c1")
        assert got.digest_mode == "daily" and len(got.channels) == 1

    def test_should_notify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreference()
        pref = NotificationPreference(consumer_id="c1", channels=[NotificationChannel(channel_type="email", target="a@b.com"), NotificationChannel(channel_type="slack", target="#alerts", enabled=False)])
        svc.set_preference("inst-1", pref)
        channels = svc.should_notify("inst-1", "c1", "security")
        assert len(channels) == 1 and channels[0].channel_type == "email"

    def test_mute_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreference()
        svc.set_preference("inst-1", NotificationPreference(consumer_id="c1", channels=[NotificationChannel(channel_type="email", target="a@b.com")]))
        svc.mute("inst-1", "c1", "billing")
        assert len(svc.should_notify("inst-1", "c1", "billing")) == 0
        svc.unmute("inst-1", "c1", "billing")
        assert len(svc.should_notify("inst-1", "c1", "billing")) == 1

    def test_invalid_digest(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreference()
        with pytest.raises(ValueError, match="Invalid digest_mode"):
            svc.set_preference("inst-1", NotificationPreference(consumer_id="c1", digest_mode="weekly"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerNotificationPreference()
        svc.set_preference("inst-1", NotificationPreference(consumer_id="c1"))
        assert svc.get_preference("inst-2", "c1") is None
