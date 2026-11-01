from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_response_transformer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformer, TransformConfig, TransformRule,
)

class TestResponseTransformer:
    def test_rename(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformer()
        svc.configure("inst-1", TransformConfig(consumer_id="c1", rules=[TransformRule(rule_id="r1", operation="rename", source_field="name", target_field="full_name")]))
        result = svc.transform("inst-1", "c1", {"name": "Alice", "id": "1"})
        assert result["full_name"] == "Alice" and "name" not in result

    def test_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformer()
        svc.configure("inst-1", TransformConfig(consumer_id="c1", rules=[TransformRule(rule_id="r1", operation="remove", source_field="internal_id")]))
        result = svc.transform("inst-1", "c1", {"id": "1", "internal_id": "secret"})
        assert "internal_id" not in result

    def test_mask(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformer()
        svc.configure("inst-1", TransformConfig(consumer_id="c1", rules=[TransformRule(rule_id="r1", operation="mask", source_field="ssn")]))
        result = svc.transform("inst-1", "c1", {"ssn": "123-45-6789"})
        assert result["ssn"].startswith("***") and result["ssn"].endswith("6789")

    def test_disabled_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformer()
        svc.configure("inst-1", TransformConfig(consumer_id="c1", enabled=False, rules=[TransformRule(rule_id="r1", operation="remove", source_field="x")]))
        result = svc.transform("inst-1", "c1", {"x": "keep"})
        assert "x" in result

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformer()
        svc.configure("inst-1", TransformConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
