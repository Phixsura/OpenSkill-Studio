from app.services.app_api_developer_api_webhook_payload_inspector import AppAPIDeveloperAPIWebhookPayloadInspector

class TestPayloadInspector:
    def test_inspect_valid(self):
        p = AppAPIDeveloperAPIWebhookPayloadInspector()
        r = p.inspect("inst-1", "i1", "push", '{"name": "test", "data": [1,2]}')
        assert r.field_count == 2
        assert r.has_nested is True
        assert not r.validation_errors

    def test_inspect_invalid_json(self):
        p = AppAPIDeveloperAPIWebhookPayloadInspector()
        r = p.inspect("inst-1", "i1", "push", "not json")
        assert len(r.validation_errors) == 1

    def test_oversized(self):
        p = AppAPIDeveloperAPIWebhookPayloadInspector(max_payload_bytes=10)
        r = p.inspect("inst-1", "i1", "push", '{"a": "longvalue"}')
        assert any("exceeds" in e for e in r.validation_errors)

    def test_with_errors(self):
        p = AppAPIDeveloperAPIWebhookPayloadInspector()
        p.inspect("inst-1", "i1", "push", '{"ok": true}')
        p.inspect("inst-1", "i2", "push", "bad")
        assert len(p.with_errors("inst-1")) == 1

    def test_isolation(self):
        p = AppAPIDeveloperAPIWebhookPayloadInspector()
        p.inspect("inst-1", "i1", "push", '{}')
        assert len(p.recent("inst-2")) == 0
