from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_body_size_limit import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimit

class TestRequestBodySizeLimit:
    def test_allow_under_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimit()
        svc.set_limit("inst-1", "/api", "POST", 10000)
        r = svc.check("inst-1", "/api", "POST", 5000)
        assert r["allowed"] is True

    def test_reject_over_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimit()
        svc.set_limit("inst-1", "/api", "POST", 1024)
        r = svc.check("inst-1", "/api", "POST", 5000)
        assert r["allowed"] is False

    def test_default_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimit(default_max_bytes=2048)
        r = svc.check("inst-1", "/api", "POST", 1000)
        assert r["allowed"] is True and r["max_bytes"] == 2048

    def test_rejection_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimit()
        svc.set_limit("inst-1", "/api", "POST", 1024)
        svc.check("inst-1", "/api", "POST", 500)
        svc.check("inst-1", "/api", "POST", 5000)
        l = svc._limits[("inst-1", "POST", "/api")]
        assert l.rejection_rate == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimit()
        svc.set_limit("inst-1", "/api", "POST", 1024)
        assert len(svc.list_limits("inst-2")) == 0
