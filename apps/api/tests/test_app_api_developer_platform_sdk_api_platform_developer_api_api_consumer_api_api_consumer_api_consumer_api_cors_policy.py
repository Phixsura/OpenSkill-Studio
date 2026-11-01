import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_cors_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy, CORSPolicy,
)

class TestConsumerApiCorsPolicy:
    def test_allowed_origin(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy()
        svc.set_policy("inst-1", CORSPolicy(consumer_id="c1", allowed_origins=["https://app.example.com"]))
        result = svc.check("inst-1", "c1", "https://app.example.com", "GET")
        assert result.allowed and "Access-Control-Allow-Origin" in result.headers

    def test_blocked_origin(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy()
        svc.set_policy("inst-1", CORSPolicy(consumer_id="c1", allowed_origins=["https://app.example.com"]))
        result = svc.check("inst-1", "c1", "https://evil.com", "GET")
        assert not result.allowed

    def test_wildcard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy()
        svc.set_policy("inst-1", CORSPolicy(consumer_id="c1", allowed_origins=["*"]))
        result = svc.check("inst-1", "c1", "https://anything.com", "POST")
        assert result.allowed

    def test_credentials_with_wildcard_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy()
        with pytest.raises(ValueError, match="wildcard origin with credentials"):
            svc.set_policy("inst-1", CORSPolicy(consumer_id="c1", allowed_origins=["*"], allow_credentials=True))

    def test_method_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy()
        svc.set_policy("inst-1", CORSPolicy(consumer_id="c1", allowed_origins=["https://app.com"], allowed_methods=["GET"]))
        assert not svc.check("inst-1", "c1", "https://app.com", "DELETE").allowed

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiCorsPolicy()
        svc.set_policy("inst-1", CORSPolicy(consumer_id="c1", allowed_origins=["https://app.com"]))
        assert svc.get_policy("inst-2", "c1") is None
