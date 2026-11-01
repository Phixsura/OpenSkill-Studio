from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_notification_digest import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiNotificationDigest, Notification,
)

class TestNotificationDigest:
    def test_add_and_digest(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiNotificationDigest()
        svc.add_notification("inst-1", "c1", Notification(notification_id="n1", category="alert", title="High error rate"))
        svc.add_notification("inst-1", "c1", Notification(notification_id="n2", category="changelog", title="v2.0 released"))
        digest = svc.generate_digest("inst-1", "c1", "d1", "daily")
        assert len(digest.notifications) == 2
        assert digest.by_category["alert"] == 1

    def test_digest_clears_queue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiNotificationDigest()
        svc.add_notification("inst-1", "c1", Notification(notification_id="n1", category="usage", title="80% quota"))
        svc.generate_digest("inst-1", "c1", "d1", "daily")
        assert svc.unread_count("inst-1", "c1") == 0

    def test_invalid_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiNotificationDigest()
        import pytest
        with pytest.raises(ValueError):
            svc.add_notification("inst-1", "c1", Notification(notification_id="n1", category="bad", title="X"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiNotificationDigest()
        svc.add_notification("inst-1", "c1", Notification(notification_id="n1", category="alert", title="X"))
        assert svc.notification_count("inst-2") == 0
