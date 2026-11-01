import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_notification_preference import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreference, NotificationPreference,
)

class TestConsumerNotificationPreference:
    def test_default_notifies(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreference()
        assert svc.should_notify("inst-1", "c1", "order.created") is True

    def test_quiet_hours(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreference()
        svc.set_preference("inst-1", NotificationPreference(consumer_id="c1", quiet_hours_start=22, quiet_hours_end=6))
        assert svc.should_notify("inst-1", "c1", "alert", current_hour=23) is False
        assert svc.should_notify("inst-1", "c1", "alert", current_hour=10) is True

    def test_channel_opt_out(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreference()
        svc.set_preference("inst-1", NotificationPreference(consumer_id="c1", channels={"marketing": False, "alerts": True}))
        assert svc.should_notify("inst-1", "c1", "marketing") is False
        assert svc.should_notify("inst-1", "c1", "alerts") is True

    def test_invalid_frequency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreference()
        with pytest.raises(ValueError, match="Invalid frequency"):
            svc.set_preference("inst-1", NotificationPreference(consumer_id="c1", frequency="never"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerNotificationPreference()
        svc.set_preference("inst-1", NotificationPreference(consumer_id="c1"))
        assert svc.consumer_count("inst-2") == 0
