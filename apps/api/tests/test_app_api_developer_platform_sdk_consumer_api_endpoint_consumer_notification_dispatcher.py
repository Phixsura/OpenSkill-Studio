import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_consumer_notification_dispatcher import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher, Notification,
)

class TestNotificationDispatcher:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_dispatch(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher()
        svc.configure_channels("inst-1", "c1", ["email", "slack", "in_app"])
        result = svc.dispatch("inst-1", Notification(notification_id="n1", consumer_id="c1", title="Alert", message="High error rate", severity="warning", channels=["email", "slack"]), self._now())
        assert result.success and "email" in result.channels_sent

    def test_unread(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher()
        svc.dispatch("inst-1", Notification(notification_id="n1", consumer_id="c1", title="A", message="B"), self._now())
        svc.dispatch("inst-1", Notification(notification_id="n2", consumer_id="c1", title="C", message="D"), self._now())
        assert len(svc.get_unread("inst-1", "c1")) == 2

    def test_mark_read(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher()
        svc.dispatch("inst-1", Notification(notification_id="n1", consumer_id="c1", title="A", message="B"), self._now())
        svc.mark_read("inst-1", "c1", "n1")
        assert len(svc.get_unread("inst-1", "c1")) == 0

    def test_default_channel(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher()
        result = svc.dispatch("inst-1", Notification(notification_id="n1", consumer_id="c1", title="A", message="B"), self._now())
        assert "in_app" in result.channels_sent  # default

    def test_invalid_severity(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher()
        with pytest.raises(ValueError, match="Invalid severity"):
            svc.dispatch("inst-1", Notification(notification_id="n1", consumer_id="c1", title="A", message="B", severity="urgent"), self._now())

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointConsumerNotificationDispatcher()
        svc.dispatch("inst-1", Notification(notification_id="n1", consumer_id="c1", title="A", message="B"), self._now())
        assert len(svc.get_unread("inst-2", "c1")) == 0
