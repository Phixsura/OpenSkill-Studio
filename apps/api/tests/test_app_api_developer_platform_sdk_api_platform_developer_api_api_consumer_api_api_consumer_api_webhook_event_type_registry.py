import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_event_type_registry import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistry, EventTypeEntry,
)

class TestWebhookEventTypeRegistry:
    def test_register(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistry()
        e = svc.register("inst-1", EventTypeEntry(event_type="order.created", category="order", description="When an order is created"))
        assert e.event_type == "order.created"

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistry()
        svc.register("inst-1", EventTypeEntry(event_type="order.created", category="order"))
        svc.register("inst-1", EventTypeEntry(event_type="user.signup", category="user"))
        assert len(svc.search("inst-1", "order")) == 1

    def test_deprecate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistry()
        svc.register("inst-1", EventTypeEntry(event_type="old.event", category="system"))
        svc.deprecate("inst-1", "old.event")
        assert len(svc.active_types("inst-1")) == 0

    def test_duplicate_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistry()
        svc.register("inst-1", EventTypeEntry(event_type="x", category="system"))
        with pytest.raises(ValueError, match="already registered"):
            svc.register("inst-1", EventTypeEntry(event_type="x", category="system"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventTypeRegistry()
        svc.register("inst-1", EventTypeEntry(event_type="x", category="system"))
        assert len(svc.list_types("inst-2")) == 0
