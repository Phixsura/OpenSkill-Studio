import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_timeout_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicy, TimeoutPolicy,
)

class TestRequestTimeoutPolicy:
    def test_custom_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicy()
        svc.set_policy("inst-1", TimeoutPolicy(endpoint="/slow", method="GET", timeout_ms=60000))
        assert svc.get_timeout("inst-1", "GET", "/slow") == 60000

    def test_default_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicy(default_timeout_ms=15000)
        assert svc.get_timeout("inst-1", "GET", "/any") == 15000

    def test_retry_on_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicy()
        svc.set_policy("inst-1", TimeoutPolicy(endpoint="/api", method="POST", retry_on_timeout=True, max_retries=2))
        assert svc.should_retry("inst-1", "POST", "/api", 0) is True
        assert svc.should_retry("inst-1", "POST", "/api", 2) is False

    def test_invalid_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicy()
        with pytest.raises(ValueError, match="timeout"):
            svc.set_policy("inst-1", TimeoutPolicy(endpoint="/api", method="GET", timeout_ms=50))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicy()
        svc.set_policy("inst-1", TimeoutPolicy(endpoint="/api", method="GET"))
        assert len(svc.list_policies("inst-2")) == 0
