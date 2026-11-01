from app.services.app_api_developer_platform_sdk_api_platform_webhook_event_catalog import AppAPIDeveloperPlatformSDKApiPlatformWebhookEventCatalog

class TestWebhookEventCatalog:
    def test_add(self):
        c = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventCatalog()
        e = c.add("inst-1", "order.created", "orders", "Order was created", "1.0", '{"order_id": "123"}')
        assert e.category == "orders"

    def test_search(self):
        c = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventCatalog()
        c.add("inst-1", "order.created", "orders", "Order was created", "1.0")
        c.add("inst-1", "user.signup", "users", "User signed up", "1.0")
        assert len(c.search("inst-1", "order")) == 1

    def test_by_category(self):
        c = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventCatalog()
        c.add("inst-1", "order.created", "orders", "Created", "1.0")
        c.add("inst-1", "order.updated", "orders", "Updated", "1.0")
        c.add("inst-1", "user.signup", "users", "Signup", "1.0")
        assert len(c.by_category("inst-1", "orders")) == 2

    def test_categories(self):
        c = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventCatalog()
        c.add("inst-1", "a", "orders", "A", "1.0")
        c.add("inst-1", "b", "users", "B", "1.0")
        assert c.categories("inst-1") == {"orders": 1, "users": 1}

    def test_isolation(self):
        c = AppAPIDeveloperPlatformSDKApiPlatformWebhookEventCatalog()
        c.add("inst-1", "a", "orders", "A", "1.0")
        assert len(c.all_events("inst-2")) == 0
