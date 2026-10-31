import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_webhook_template import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate, WebhookTemplate,
)

class TestConsumerWebhookTemplate:
    def test_create_and_render(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate()
        svc.create("inst-1", WebhookTemplate(template_id="t1", name="Order", body_template='{"order_id":"{{order_id}}","total":{{total}}}'))
        result = svc.render("inst-1", "t1", {"order_id": "O123", "total": "99.99"})
        assert '"O123"' in result.body and "99.99" in result.body

    def test_missing_vars(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate()
        svc.create("inst-1", WebhookTemplate(template_id="t1", name="T", body_template="Hello {{name}}"))
        result = svc.render("inst-1", "t1", {})
        assert "name" in result.missing_vars and "{{name}}" in result.body

    def test_header_templates(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate()
        svc.create("inst-1", WebhookTemplate(template_id="t1", name="T", body_template="", header_templates={"X-Event": "{{event_type}}"}))
        result = svc.render("inst-1", "t1", {"event_type": "order.created"})
        assert result.headers["X-Event"] == "order.created"

    def test_list_variables(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate()
        svc.create("inst-1", WebhookTemplate(template_id="t1", name="T", body_template="{{a}} {{b}}", header_templates={"X": "{{c}}"}))
        vars = svc.list_variables("inst-1", "t1")
        assert vars == ["a", "b", "c"]

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate()
        svc.create("inst-1", WebhookTemplate(template_id="t1", name="T"))
        with pytest.raises(ValueError, match="already exists"):
            svc.create("inst-1", WebhookTemplate(template_id="t1", name="T2"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate()
        svc.create("inst-1", WebhookTemplate(template_id="t1", name="T"))
        assert len(svc.list_templates("inst-2")) == 0
