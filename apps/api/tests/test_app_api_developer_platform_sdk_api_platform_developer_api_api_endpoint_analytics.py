from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_endpoint_analytics import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalytics

class TestApiEndpointAnalytics:
    def test_record_and_metrics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalytics()
        svc.record("inst-1", "GET", "/users", "c1", 200, 50)
        svc.record("inst-1", "GET", "/users", "c2", 500, 100)
        m = svc.get_metrics("inst-1", "GET", "/users")
        assert m.total_requests == 2
        assert m.error_rate == 50.0
        assert m.avg_latency == 75.0

    def test_top_consumers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalytics()
        for _ in range(10): svc.record("inst-1", "GET", "/api", "c1", 200, 10)
        for _ in range(5): svc.record("inst-1", "GET", "/api", "c2", 200, 10)
        m = svc.get_metrics("inst-1", "GET", "/api")
        top = m.top_consumers
        assert top[0] == ("c1", 10)

    def test_high_error(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalytics()
        for _ in range(10): svc.record("inst-1", "POST", "/bad", "c1", 500, 50)
        assert len(svc.high_error_endpoints("inst-1", 5.0)) == 1

    def test_slowest(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalytics()
        svc.record("inst-1", "GET", "/fast", "c1", 200, 10)
        svc.record("inst-1", "GET", "/slow", "c1", 200, 1000)
        slowest = svc.slowest_endpoints("inst-1", 1)
        assert slowest[0].endpoint == "/slow"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalytics()
        svc.record("inst-1", "GET", "/api", "c1", 200, 10)
        assert len(svc.list_endpoints("inst-2")) == 0
