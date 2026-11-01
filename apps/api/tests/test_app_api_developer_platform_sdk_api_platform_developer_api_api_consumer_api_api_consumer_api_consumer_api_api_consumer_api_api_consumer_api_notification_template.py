import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_notification_template import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate, NotificationTemplate,
)

class TestConsumerApiNotificationTemplate:
    def test_create_and_render(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate()
        svc.create("inst-1", NotificationTemplate(template_id="t1", name="Welcome", channel="email", subject_template="Welcome {{name}}", body_template="Hello {{name}}, welcome to {{app}}!"))
        result = svc.render("inst-1", "t1", {"name": "Alice", "app": "MyAPI"})
        assert "Alice" in result.subject and "MyAPI" in result.body

    def test_html_escaped(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate()
        svc.create("inst-1", NotificationTemplate(template_id="t1", name="Alert", channel="email", body_template="User: {{name}}"))
        result = svc.render("inst-1", "t1", {"name": "<script>alert('xss')</script>"})
        assert "&lt;script&gt;" in result.body

    def test_missing_vars(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate()
        svc.create("inst-1", NotificationTemplate(template_id="t1", name="T", channel="slack", body_template="Hi {{name}}"))
        result = svc.render("inst-1", "t1", {})
        assert "name" in result.missing_vars

    def test_variable_extraction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate()
        t = svc.create("inst-1", NotificationTemplate(template_id="t1", name="T", channel="email", subject_template="{{a}}", body_template="{{b}} {{c}}"))
        assert t.variables == ["a", "b", "c"]

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate()
        svc.create("inst-1", NotificationTemplate(template_id="t1", name="T", channel="email"))
        with pytest.raises(ValueError, match="already exists"):
            svc.create("inst-1", NotificationTemplate(template_id="t1", name="T2", channel="email"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate()
        svc.create("inst-1", NotificationTemplate(template_id="t1", name="T", channel="email"))
        assert svc.get("inst-2", "t1") is None
