from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_platform_overview_dashboard import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPlatformOverviewDashboard, PlatformOverview,
)

class TestPlatformOverviewDashboard:
    def test_healthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPlatformOverviewDashboard()
        svc.update("inst-1", PlatformOverview(total_consumers=100, overall_uptime_pct=99.99, overall_error_rate_pct=0.5))
        o = svc.get_overview("inst-1")
        assert o.health == "healthy"

    def test_critical(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPlatformOverviewDashboard()
        svc.update("inst-1", PlatformOverview(open_incidents=2))
        assert svc.get_overview("inst-1").health == "critical"

    def test_alerts(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPlatformOverviewDashboard()
        svc.update("inst-1", PlatformOverview(open_incidents=1, overall_error_rate_pct=8, webhook_success_rate=90))
        alerts = svc.alerts("inst-1")
        assert len(alerts) >= 2

    def test_revenue(self):
        o = PlatformOverview(revenue_this_month_cents=1234567)
        assert o.revenue_dollars == "$12,345.67"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPlatformOverviewDashboard()
        svc.update("inst-1", PlatformOverview(total_consumers=50))
        assert svc.get_overview("inst-2").total_consumers == 0
