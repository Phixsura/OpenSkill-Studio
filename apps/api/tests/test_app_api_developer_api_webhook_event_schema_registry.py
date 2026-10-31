import pytest
from app.services.app_api_developer_api_webhook_event_schema_registry import AppAPIDeveloperAPIWebhookEventSchemaRegistry

class TestSchemaRegistry:
    def test_register(self):
        r = AppAPIDeveloperAPIWebhookEventSchemaRegistry()
        s = r.register("inst-1", "push", "1.0", {"repo": "string", "ref": "string"}, ["repo"])
        assert s.event_type == "push"

    def test_latest(self):
        r = AppAPIDeveloperAPIWebhookEventSchemaRegistry()
        r.register("inst-1", "push", "1.0", {"repo": "string"})
        r.register("inst-1", "push", "2.0", {"repo": "string", "author": "string"})
        assert r.latest("inst-1", "push").version == "2.0"

    def test_validate(self):
        r = AppAPIDeveloperAPIWebhookEventSchemaRegistry()
        r.register("inst-1", "push", "1.0", {"repo": "string"}, ["repo"])
        assert r.validate_payload("inst-1", "push", "1.0", {"repo": "test"}) == []
        errors = r.validate_payload("inst-1", "push", "1.0", {})
        assert len(errors) == 1

    def test_list_events(self):
        r = AppAPIDeveloperAPIWebhookEventSchemaRegistry()
        r.register("inst-1", "push", "1.0", {})
        r.register("inst-1", "issue", "1.0", {})
        assert r.list_events("inst-1") == ["issue", "push"]

    def test_isolation(self):
        r = AppAPIDeveloperAPIWebhookEventSchemaRegistry()
        r.register("inst-1", "push", "1.0", {})
        assert r.list_events("inst-2") == []
