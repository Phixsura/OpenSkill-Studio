from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_playground_template import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiPlaygroundTemplate, PlaygroundTemplate,
)

class TestPlaygroundTemplate:
    def test_create_and_use(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiPlaygroundTemplate()
        svc.create_template("inst-1", PlaygroundTemplate(template_id="t1", name="Create User", method="POST", path="/users", body_template='{"name":"{{name}}"}', variables=["name"]))
        result = svc.use_template("inst-1", "t1", {"name": "Alice"})
        assert result["body"] == '{"name":"Alice"}'
        assert result["method"] == "POST"

    def test_usage_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiPlaygroundTemplate()
        svc.create_template("inst-1", PlaygroundTemplate(template_id="t1", name="Test", method="GET", path="/a"))
        svc.use_template("inst-1", "t1")
        svc.use_template("inst-1", "t1")
        top = svc.most_used("inst-1")
        assert top[0].usage_count == 2

    def test_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiPlaygroundTemplate()
        svc.create_template("inst-1", PlaygroundTemplate(template_id="t1", name="Login", method="POST", path="/auth", category="authentication"))
        svc.create_template("inst-1", PlaygroundTemplate(template_id="t2", name="List", method="GET", path="/items", category="crud"))
        cats = svc.by_category("inst-1")
        assert "authentication" in cats and "crud" in cats

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiPlaygroundTemplate()
        svc.create_template("inst-1", PlaygroundTemplate(template_id="t1", name="X", method="GET", path="/x"))
        assert len(svc.list_templates("inst-2")) == 0
