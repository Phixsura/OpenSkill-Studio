import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_webhook_event_catalog import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalog, EventType,
)

class TestWebhookEventCatalog:
    def test_register_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalog()
        svc.register("inst-1", EventType(event_id="e1", name="order.created", category="orders"))
        events = svc.list_events("inst-1")
        assert len(events) == 1

    def test_deprecate_hides(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalog()
        svc.register("inst-1", EventType(event_id="e1", name="old.event", category="legacy"))
        svc.deprecate("inst-1", "e1")
        assert len(svc.list_events("inst-1")) == 0
        assert len(svc.list_events("inst-1", include_deprecated=True)) == 1

    def test_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalog()
        svc.register("inst-1", EventType(event_id="e1", name="order.created", category="orders"))
        svc.register("inst-1", EventType(event_id="e2", name="user.signup", category="users"))
        cats = svc.by_category("inst-1")
        assert len(cats["orders"]) == 1 and len(cats["users"]) == 1

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalog()
        svc.register("inst-1", EventType(event_id="e1", name="order.created", category="orders", description="Fired when order is placed"))
        results = svc.search("inst-1", "order")
        assert len(results) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookEventCatalog()
        svc.register("inst-1", EventType(event_id="e1", name="test", category="test"))
        assert len(svc.list_events("inst-2")) == 0
