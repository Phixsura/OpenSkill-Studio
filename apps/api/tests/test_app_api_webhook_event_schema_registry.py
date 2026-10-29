from app.services.app_api_webhook_event_schema_registry import AppAPIWebhookEventSchemaRegistry

class TestRegistry:
    def test_register(self):
        r = AppAPIWebhookEventSchemaRegistry()
        s = r.register("inst-1", "push", "1.0", ["repo", "ref", "commits"], ["repo"])
        assert len(s.fields) == 3

    def test_latest(self):
        r = AppAPIWebhookEventSchemaRegistry()
        r.register("inst-1", "push", "1.0", ["repo"])
        r.register("inst-1", "push", "2.0", ["repo", "branch"])
        assert r.latest("inst-1", "push").version == "2.0"

    def test_deprecate(self):
        r = AppAPIWebhookEventSchemaRegistry()
        r.register("inst-1", "push", "1.0", ["repo"])
        r.deprecate("inst-1", "push", "1.0")
        assert r.latest("inst-1", "push") is None

    def test_isolation(self):
        r = AppAPIWebhookEventSchemaRegistry()
        r.register("inst-1", "push", "1.0", ["repo"])
        assert r.list_schemas("inst-2") == []
