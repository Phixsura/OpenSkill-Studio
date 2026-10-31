import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_response_transformer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer, TransformConfig,
)

class TestConsumerApiResponseTransformer:
    def test_rename_fields(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer()
        svc.set_config("inst-1", TransformConfig(consumer_id="c1", rename_fields={"user_id": "id"}, wrap_in_envelope=False))
        result, meta = svc.transform("inst-1", "c1", {"user_id": "123", "name": "Alice"})
        assert "id" in result and result["id"] == "123" and meta.fields_renamed == 1

    def test_exclude_fields(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer()
        svc.set_config("inst-1", TransformConfig(consumer_id="c1", exclude_fields={"internal_id", "debug"}, wrap_in_envelope=False))
        result, meta = svc.transform("inst-1", "c1", {"name": "Alice", "internal_id": "x", "debug": "y"})
        assert "internal_id" not in result and meta.fields_excluded == 2

    def test_include_only(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer()
        svc.set_config("inst-1", TransformConfig(consumer_id="c1", include_only={"name", "email"}, wrap_in_envelope=False))
        result, _ = svc.transform("inst-1", "c1", {"name": "A", "email": "a@b.com", "secret": "x"})
        assert set(result.keys()) == {"name", "email"}

    def test_envelope(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer()
        svc.set_config("inst-1", TransformConfig(consumer_id="c1", wrap_in_envelope=True))
        result, _ = svc.transform("inst-1", "c1", {"name": "A"})
        assert "data" in result and result["data"]["name"] == "A"

    def test_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer()
        result, meta = svc.transform("inst-1", "c1", {"name": "A"})
        assert result == {"name": "A"} and meta.fields_renamed == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiResponseTransformer()
        svc.set_config("inst-1", TransformConfig(consumer_id="c1", exclude_fields={"x"}))
        assert svc.get_config("inst-2", "c1") is None
