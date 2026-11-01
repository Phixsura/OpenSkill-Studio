import pytest
from app.services.app_api_developer_platform_sdk_webhook_consumer_notification_channel import AppAPIDeveloperPlatformSDKWebhookConsumerNotificationChannel

class TestNotificationChannel:
    def test_add(self):
        n = AppAPIDeveloperPlatformSDKWebhookConsumerNotificationChannel()
        c = n.add("inst-1", "ch1", "c1", "email", "dev@acme.com")
        assert c.channel_type == "email"

    def test_webhook_https(self):
        n = AppAPIDeveloperPlatformSDKWebhookConsumerNotificationChannel()
        with pytest.raises(ValueError):
            n.add("inst-1", "ch1", "c1", "webhook", "http://bad.com")

    def test_notify(self):
        n = AppAPIDeveloperPlatformSDKWebhookConsumerNotificationChannel()
        n.add("inst-1", "ch1", "c1", "slack", "#alerts")
        n.notify("inst-1", "ch1")
        assert n.all_channels("inst-1")[0].notifications_sent == 1

    def test_for_consumer(self):
        n = AppAPIDeveloperPlatformSDKWebhookConsumerNotificationChannel()
        n.add("inst-1", "ch1", "c1", "email", "a@b.com")
        n.add("inst-1", "ch2", "c2", "slack", "#c2")
        assert len(n.for_consumer("inst-1", "c1")) == 1

    def test_isolation(self):
        n = AppAPIDeveloperPlatformSDKWebhookConsumerNotificationChannel()
        n.add("inst-1", "ch1", "c1", "email", "a@b.com")
        assert len(n.all_channels("inst-2")) == 0
