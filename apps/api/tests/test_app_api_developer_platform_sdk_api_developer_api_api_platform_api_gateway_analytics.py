from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_api_gateway_analytics import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalytics

class TestGatewayAnalytics:
    def test_excellent(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalytics()
        a = g.update("inst-1", total_requests=1000000, total_errors=50, avg_latency_ms=30, p99_latency_ms=150)
        assert a.health == "excellent"
        assert a.error_rate_pct < 0.1

    def test_poor(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalytics()
        a = g.update("inst-1", total_requests=1000, total_errors=100)
        assert a.health == "poor"

    def test_default(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalytics()
        assert g.get("inst-1").error_rate_pct == 0.0

    def test_isolation(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalytics()
        g.update("inst-1", total_requests=100000)
        assert g.get("inst-2").total_requests == 0
