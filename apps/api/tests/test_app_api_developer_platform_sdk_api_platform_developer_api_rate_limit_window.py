import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_rate_limit_window import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindow, WindowConfig,
)

class TestRateLimitWindow:
    def test_allow_under_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindow()
        svc.configure("inst-1", "c1", "/api", WindowConfig(window_seconds=60, max_requests=10, burst_limit=5))
        result = svc.check("inst-1", "c1", "/api")
        assert result["allowed"] is True

    def test_window_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindow()
        svc.configure("inst-1", "c1", "/api", WindowConfig(window_seconds=60, max_requests=3, burst_limit=10))
        for _ in range(3): svc.record("inst-1", "c1", "/api")
        result = svc.check("inst-1", "c1", "/api")
        assert result["allowed"] is False
        assert result["reason"] == "window_limit"

    def test_no_config_allows(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindow()
        result = svc.check("inst-1", "c1", "/api")
        assert result["allowed"] is True
        assert result["reason"] == "no_config"

    def test_invalid_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindow()
        with pytest.raises(ValueError):
            svc.configure("inst-1", "c1", "/api", WindowConfig(window_seconds=0))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRateLimitWindow()
        svc.configure("inst-1", "c1", "/api", WindowConfig())
        assert svc.get_state("inst-2", "c1", "/api") is None
