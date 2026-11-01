import pytest
from app.services.app_api_developer_api_api_developer_api_api_webhook_event_type_registry import AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry

class TestEventTypeRegistry:
    def test_register(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry()
        t = r.register("inst-1", "order.created", "Order was created", "1.0", "resource")
        assert t.category == "resource"

    def test_invalid_category(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry()
        with pytest.raises(ValueError):
            r.register("inst-1", "x", "y", "1.0", "invalid")

    def test_deprecate(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry()
        r.register("inst-1", "old.event", "Old", "1.0", "system")
        r.deprecate("inst-1", "old.event")
        assert len(r.active_types("inst-1")) == 0

    def test_by_category(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry()
        r.register("inst-1", "order.created", "A", "1.0", "resource")
        r.register("inst-1", "system.health", "B", "1.0", "system")
        assert len(r.by_category("inst-1", "resource")) == 1

    def test_category_counts(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry()
        r.register("inst-1", "a", "A", "1.0", "resource")
        r.register("inst-1", "b", "B", "1.0", "resource")
        r.register("inst-1", "c", "C", "1.0", "system")
        assert r.category_counts("inst-1") == {"resource": 2, "system": 1}

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiWebhookEventTypeRegistry()
        r.register("inst-1", "a", "A", "1.0", "resource")
        assert len(r.all_types("inst-2")) == 0
