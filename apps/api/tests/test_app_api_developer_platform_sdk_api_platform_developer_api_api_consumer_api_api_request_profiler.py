from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_profiler import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestProfiler

class TestRequestProfiler:
    def test_record_and_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestProfiler()
        svc.record("inst-1", "/users", "GET", 50.0)
        svc.record("inst-1", "/users", "GET", 100.0)
        p = svc.get_profile("inst-1", "GET", "/users")
        assert p.avg_ms == 75.0
        assert p.min_ms == 50.0 and p.max_ms == 100.0

    def test_error_tracking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestProfiler()
        svc.record("inst-1", "/api", "POST", 50, error=True)
        svc.record("inst-1", "/api", "POST", 30, error=False)
        p = svc.get_profile("inst-1", "POST", "/api")
        assert p.error_pct == 50.0

    def test_slowest(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestProfiler()
        svc.record("inst-1", "/fast", "GET", 10)
        svc.record("inst-1", "/slow", "GET", 500)
        top = svc.slowest("inst-1", 1)
        assert top[0].endpoint == "/slow"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestProfiler()
        svc.record("inst-1", "/api", "GET", 10)
        assert len(svc.list_profiles("inst-2")) == 0
