from app.services.app_api_developer_platform_sdk_api_developer_api_platform_overview_dashboard import AppAPIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboard

class TestPlatformOverviewDashboard:
    def test_perfect_score(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboard()
        o = d.update("inst-1", uptime_pct=99.99, error_rate_pct=0.1, webhook_success_rate=99.9, security_score=100, nps=80)
        assert o.overall_score == 100

    def test_health_emoji(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboard()
        o = d.update("inst-1", platform_health="degraded")
        assert o.health_emoji == "🟡"

    def test_default(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboard()
        o = d.get("inst-1")
        assert o.total_services == 563

    def test_isolation(self):
        d = AppAPIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboard()
        d.update("inst-1", total_consumers=1000)
        assert d.get("inst-2").total_consumers == 0
