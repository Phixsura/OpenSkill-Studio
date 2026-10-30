from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_health_dashboard import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiHealthDashboard, DashboardMetrics, ConsumerSummary,
)

class TestHealthDashboard:
    def test_metrics(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiHealthDashboard()
        svc.update_metrics("inst-1", DashboardMetrics(total_consumers=50, active_consumers=45, error_rate_pct=1.5, uptime_pct=99.9))
        m = svc.get_dashboard("inst-1")
        assert m.total_consumers == 50

    def test_overall_health(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiHealthDashboard()
        svc.update_metrics("inst-1", DashboardMetrics(error_rate_pct=1.0, uptime_pct=99.95))
        assert svc.overall_health("inst-1") == "healthy"
        svc.update_metrics("inst-1", DashboardMetrics(error_rate_pct=15.0))
        assert svc.overall_health("inst-1") == "critical"

    def test_degraded_consumers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiHealthDashboard()
        svc.update_consumer("inst-1", ConsumerSummary(consumer_id="c1", health_score=95, requests_today=1000, error_rate=1.0, status="healthy"))
        svc.update_consumer("inst-1", ConsumerSummary(consumer_id="c2", health_score=40, requests_today=500, error_rate=20.0, status="critical"))
        degraded = svc.degraded_consumers("inst-1")
        assert len(degraded) == 1 and degraded[0].consumer_id == "c2"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiHealthDashboard()
        svc.update_metrics("inst-1", DashboardMetrics(total_consumers=10))
        assert svc.get_dashboard("inst-2").total_consumers == 0
