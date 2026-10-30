import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_throttle_config import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfig, ThrottleConfig,
)

class TestEndpointThrottleConfig:
    def test_allow_under_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfig()
        svc.configure("inst-1", ThrottleConfig(endpoint="/api", method="GET", max_rps=100))
        result = svc.check("inst-1", "GET", "/api", 50)
        assert result["throttled"] is False

    def test_throttle_over_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfig()
        svc.configure("inst-1", ThrottleConfig(endpoint="/api", method="POST", max_rps=10, throttle_action="queue"))
        result = svc.check("inst-1", "POST", "/api", 15)
        assert result["throttled"] is True and result["action"] == "queue"

    def test_burst_allowance(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfig()
        svc.configure("inst-1", ThrottleConfig(endpoint="/api", method="GET", max_rps=100, burst_size=20))
        result = svc.check("inst-1", "GET", "/api", 115)
        assert result["throttled"] is False  # within burst

    def test_invalid_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfig()
        with pytest.raises(ValueError, match="Invalid action"):
            svc.configure("inst-1", ThrottleConfig(endpoint="/api", method="GET", max_rps=100, throttle_action="drop"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfig()
        svc.configure("inst-1", ThrottleConfig(endpoint="/api", method="GET", max_rps=100))
        assert len(svc.list_configs("inst-2")) == 0
