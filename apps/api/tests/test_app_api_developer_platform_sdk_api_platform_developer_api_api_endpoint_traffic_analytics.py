from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_endpoint_traffic_analytics import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalytics

class TestEndpointTrafficAnalytics:
    def test_record_and_rps(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalytics()
        for _ in range(300): svc.record("inst-1", "/api", "GET", "c1", 200)
        w = svc.get_traffic("inst-1", "/api", "GET")
        assert w.request_count == 300
        assert w.rps == 1.0  # 300 / (5 * 60)

    def test_error_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalytics()
        for _ in range(80): svc.record("inst-1", "/api", "POST", "c1", 200)
        for _ in range(20): svc.record("inst-1", "/api", "POST", "c1", 500)
        w = svc.get_traffic("inst-1", "/api", "POST")
        assert w.error_rate == 20.0

    def test_hottest(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalytics()
        for _ in range(100): svc.record("inst-1", "/hot", "GET", "c1", 200)
        for _ in range(10): svc.record("inst-1", "/cold", "GET", "c1", 200)
        hot = svc.hottest_endpoints("inst-1", 1)
        assert hot[0].endpoint == "/hot"

    def test_unique_consumers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalytics()
        svc.record("inst-1", "/api", "GET", "c1", 200)
        svc.record("inst-1", "/api", "GET", "c2", 200)
        svc.record("inst-1", "/api", "GET", "c1", 200)
        w = svc.get_traffic("inst-1", "/api", "GET")
        assert len(w.unique_consumers) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointTrafficAnalytics()
        svc.record("inst-1", "/api", "GET", "c1", 200)
        assert len(svc.list_endpoints("inst-2")) == 0
