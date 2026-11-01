import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_header_injector import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjector, InjectionConfig, HeaderInjectionRule,
)

class TestRequestHeaderInjector:
    def test_inject_headers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjector()
        svc.configure("inst-1", InjectionConfig(consumer_id="c1", rules=[HeaderInjectionRule("r1", "X-Request-Source", "api-gateway")]))
        result = svc.inject("inst-1", "c1", {"Content-Type": "application/json"})
        assert result["X-Request-Source"] == "api-gateway"
        assert result["Content-Type"] == "application/json"

    def test_no_override_by_default(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjector()
        svc.configure("inst-1", InjectionConfig(consumer_id="c1", rules=[HeaderInjectionRule("r1", "X-Custom", "new")]))
        result = svc.inject("inst-1", "c1", {"X-Custom": "existing"})
        assert result["X-Custom"] == "existing"

    def test_override_when_enabled(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjector()
        svc.configure("inst-1", InjectionConfig(consumer_id="c1", rules=[HeaderInjectionRule("r1", "X-Custom", "new", override=True)]))
        result = svc.inject("inst-1", "c1", {"X-Custom": "existing"})
        assert result["X-Custom"] == "new"

    def test_forbidden_header(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjector()
        with pytest.raises(ValueError, match="forbidden"):
            svc.configure("inst-1", InjectionConfig(consumer_id="c1", rules=[HeaderInjectionRule("r1", "Host", "evil.com")]))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjector()
        svc.configure("inst-1", InjectionConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
