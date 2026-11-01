from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_shadow_mode import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowMode, ShadowConfig, ShadowResult,
)

class TestRequestShadowMode:
    def test_configure_and_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowMode()
        svc.configure("inst-1", ShadowConfig(endpoint="/users", method="GET", shadow_version="v2"))
        assert svc.is_shadowed("inst-1", "GET", "/users") is True
        assert svc.is_shadowed("inst-1", "GET", "/orders") is False

    def test_match_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowMode()
        svc.record_result("inst-1", ShadowResult(request_id="r1", endpoint="/api", primary_status=200, shadow_status=200, match=True))
        svc.record_result("inst-1", ShadowResult(request_id="r2", endpoint="/api", primary_status=200, shadow_status=500, match=False, diff_fields=["status"]))
        assert svc.match_rate("inst-1") == 50.0

    def test_mismatches(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowMode()
        svc.record_result("inst-1", ShadowResult(request_id="r1", endpoint="/api", primary_status=200, shadow_status=200, match=True))
        svc.record_result("inst-1", ShadowResult(request_id="r2", endpoint="/api", primary_status=200, shadow_status=500, match=False))
        mm = svc.mismatches("inst-1")
        assert len(mm) == 1

    def test_disabled_not_shadowed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowMode()
        svc.configure("inst-1", ShadowConfig(endpoint="/api", method="GET", shadow_version="v2", active=False))
        assert svc.is_shadowed("inst-1", "GET", "/api") is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestShadowMode()
        svc.configure("inst-1", ShadowConfig(endpoint="/api", method="GET", shadow_version="v2"))
        assert len(svc.list_configs("inst-2")) == 0
