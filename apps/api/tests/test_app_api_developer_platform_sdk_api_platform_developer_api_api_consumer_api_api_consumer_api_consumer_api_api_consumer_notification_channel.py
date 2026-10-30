import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_notification_channel import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel, NotificationChannel, Notification,
)

class TestConsumerApiNotificationChannel:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_add_and_send(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel()
        svc.add_channel("inst-1", NotificationChannel(channel_id="ch1", consumer_id="c1", channel_type="email", destination="a@b.com"))
        svc.verify("inst-1", "c1", "ch1")
        n = svc.send("inst-1", Notification(notification_id="n1", consumer_id="c1", channel_id="ch1", title="Alert", message="Test"), self._now())
        assert n.delivered

    def test_unverified_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel()
        svc.add_channel("inst-1", NotificationChannel(channel_id="ch1", consumer_id="c1", channel_type="email", destination="a@b.com"))
        with pytest.raises(ValueError, match="not verified"):
            svc.send("inst-1", Notification(notification_id="n1", consumer_id="c1", channel_id="ch1", title="X", message="Y"), self._now())

    def test_disabled_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel()
        svc.add_channel("inst-1", NotificationChannel(channel_id="ch1", consumer_id="c1", channel_type="email", destination="a@b.com", verified=True, enabled=False))
        with pytest.raises(ValueError, match="disabled"):
            svc.send("inst-1", Notification(notification_id="n1", consumer_id="c1", channel_id="ch1", title="X", message="Y"), self._now())

    def test_webhook_https(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel()
        with pytest.raises(ValueError, match="HTTPS"):
            svc.add_channel("inst-1", NotificationChannel(channel_id="ch1", consumer_id="c1", channel_type="webhook", destination="http://insecure.com"))

    def test_list_channels(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel()
        svc.add_channel("inst-1", NotificationChannel(channel_id="ch1", consumer_id="c1", channel_type="email", destination="a@b.com"))
        svc.add_channel("inst-1", NotificationChannel(channel_id="ch2", consumer_id="c1", channel_type="slack", destination="#alerts"))
        assert len(svc.list_channels("inst-1", "c1")) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerNotificationChannel()
        svc.add_channel("inst-1", NotificationChannel(channel_id="ch1", consumer_id="c1", channel_type="email", destination="a@b.com"))
        assert len(svc.list_channels("inst-2", "c1")) == 0
