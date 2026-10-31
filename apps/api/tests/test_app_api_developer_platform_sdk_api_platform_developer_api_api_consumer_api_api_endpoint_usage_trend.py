from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_usage_trend import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrend

class TestEndpointUsageTrend:
    def test_growing(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrend()
        for i, count in enumerate([100, 120, 150, 200, 300, 500]):
            svc.record("inst-1", "/api", "GET", f"2024-0{i+1}", count)
        trends = svc.growing_endpoints("inst-1")
        assert len(trends) == 1

    def test_declining(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrend()
        for i, count in enumerate([500, 400, 300, 200, 100, 50]):
            svc.record("inst-1", "/old", "GET", f"2024-0{i+1}", count)
        assert len(svc.declining_endpoints("inst-1")) == 1

    def test_stable(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrend()
        for i in range(6):
            svc.record("inst-1", "/api", "GET", f"2024-0{i+1}", 100)
        t = svc.list_trends("inst-1")[0]
        assert t.trend_direction == "stable"

    def test_total(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrend()
        svc.record("inst-1", "/api", "GET", "2024-01", 100)
        svc.record("inst-1", "/api", "GET", "2024-02", 200)
        assert svc.list_trends("inst-1")[0].total_requests == 300

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointUsageTrend()
        svc.record("inst-1", "/api", "GET", "2024-01", 100)
        assert len(svc.list_trends("inst-2")) == 0
