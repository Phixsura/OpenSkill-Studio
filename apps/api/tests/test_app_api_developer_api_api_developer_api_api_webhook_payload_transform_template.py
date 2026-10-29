import pytest
from app.services.app_api_developer_api_api_developer_api_api_webhook_payload_transform_template import AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplate

class TestTransformTemplate:
    def test_create(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplate()
        tpl = t.create("inst-1", "t1", "Standard", '{"event": "{{event_type}}", "source": "{{source}}"}')
        assert tpl.variables == ["event_type", "source"]

    def test_apply(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplate()
        t.create("inst-1", "t1", "Simple", 'Event: {{type}} from {{origin}}')
        result = t.apply("inst-1", "t1", {"type": "push", "origin": "github"})
        assert result == "Event: push from github"

    def test_missing_var(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplate()
        t.create("inst-1", "t1", "Tpl", "Hello {{name}}")
        result = t.apply("inst-1", "t1", {})
        assert result == "Hello "

    def test_usage_count(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplate()
        t.create("inst-1", "t1", "Tpl", "{{x}}")
        t.apply("inst-1", "t1", {"x": "1"})
        t.apply("inst-1", "t1", {"x": "2"})
        assert t.list_templates("inst-1")[0].usage_count == 2

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplate()
        t.create("inst-1", "t1", "Tpl", "{{x}}")
        assert len(t.list_templates("inst-2")) == 0
