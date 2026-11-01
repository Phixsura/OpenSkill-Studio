from app.services.app_api_developer_platform_sdk_api_platform_api_developer_api_usage_dashboard import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboard

class TestAPIUsageDashboard:
    def test_excellent(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboard()
        dd = d.update("inst-1", total_requests_24h=100000, error_rate_pct=0.1, p99_latency_ms=150)
        assert dd.health == "excellent"

    def test_growth(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboard()
        dd = d.update("inst-1", total_requests_24h=20000, total_requests_7d=70000)
        # avg daily = 10000, today = 20000 → +100%
        assert dd.daily_growth_pct == 100.0

    def test_default(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboard()
        assert d.get("inst-1").total_requests_24h == 0

    def test_isolation(self):
        d = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboard()
        d.update("inst-1", total_requests_24h=100000)
        assert d.get("inst-2").total_requests_24h == 0
