import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_webhook_destination_registry import AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistry

class TestDestinationRegistry:
    def test_register(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistry()
        d = r.register("inst-1", "d1", "https://hook.example.com", "Production", ["push", "issue"])
        assert d.active is True
        assert len(d.subscribed_events) == 2

    def test_https_required(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistry()
        with pytest.raises(ValueError):
            r.register("inst-1", "d1", "http://bad.com", "Bad")

    def test_deactivate(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistry()
        r.register("inst-1", "d1", "https://a.com", "Test")
        r.deactivate("inst-1", "d1")
        assert len(r.active_destinations("inst-1")) == 0

    def test_delivery(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistry()
        r.register("inst-1", "d1", "https://a.com", "Test")
        r.record_delivery("inst-1", "d1")
        assert r.all_destinations("inst-1")[0].total_deliveries == 1

    def test_isolation(self):
        r = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistry()
        r.register("inst-1", "d1", "https://a.com", "Test")
        assert len(r.all_destinations("inst-2")) == 0
