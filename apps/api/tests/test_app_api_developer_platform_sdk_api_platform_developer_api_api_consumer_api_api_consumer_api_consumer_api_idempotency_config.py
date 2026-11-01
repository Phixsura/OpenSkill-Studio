import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_idempotency_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig, IdempotencyConfig,
)

class TestConsumerApiIdempotencyConfig:
    def test_valid_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig()
        svc.set_config("inst-1", IdempotencyConfig(consumer_id="c1"))
        result = svc.check("inst-1", "c1", "POST", "idem-key-12345")
        assert result.valid and result.reason == "valid"

    def test_missing_key_enforced(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig()
        svc.set_config("inst-1", IdempotencyConfig(consumer_id="c1", enforce=True))
        result = svc.check("inst-1", "c1", "POST", None)
        assert not result.valid and result.reason == "key_missing"

    def test_missing_key_optional(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig()
        svc.set_config("inst-1", IdempotencyConfig(consumer_id="c1", enforce=False))
        result = svc.check("inst-1", "c1", "POST", None)
        assert result.valid and result.reason == "key_optional"

    def test_key_too_long(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig()
        svc.set_config("inst-1", IdempotencyConfig(consumer_id="c1", max_key_length=20))
        result = svc.check("inst-1", "c1", "POST", "a" * 25)
        assert not result.valid and result.reason == "key_too_long"

    def test_get_not_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig()
        svc.set_config("inst-1", IdempotencyConfig(consumer_id="c1"))
        result = svc.check("inst-1", "c1", "GET", None)
        assert result.valid and result.reason == "method_not_required"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig()
        svc.set_config("inst-1", IdempotencyConfig(consumer_id="c1", enforce=True))
        result = svc.check("inst-2", "c1", "POST", None)
        assert result.valid  # no config for inst-2
