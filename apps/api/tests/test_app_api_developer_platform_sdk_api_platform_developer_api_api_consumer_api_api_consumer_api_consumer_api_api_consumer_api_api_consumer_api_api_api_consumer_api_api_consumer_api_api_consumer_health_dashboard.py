import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_consumer_api_api_consumer_health_dashboard import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard,
)

class TestConsumerHealthDashboard:
    def test_all_healthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard()
        dash = svc.compute("inst-1", "c1", error_rate=0.1, avg_latency_ms=100, uptime_pct=99.99)
        assert dash.overall_status == "healthy" and dash.health_score == 100

    def test_degraded(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard()
        dash = svc.compute("inst-1", "c1", error_rate=2.0, avg_latency_ms=100, uptime_pct=99.99)
        assert dash.overall_status == "degraded"

    def test_critical(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard()
        dash = svc.compute("inst-1", "c1", error_rate=10, avg_latency_ms=2000, uptime_pct=95)
        assert dash.overall_status == "critical" and dash.health_score == 0

    def test_list_critical(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard()
        svc.compute("inst-1", "c1", error_rate=0.1, avg_latency_ms=50, uptime_pct=99.99)
        svc.compute("inst-1", "c2", error_rate=10, avg_latency_ms=2000, uptime_pct=90)
        critical = svc.list_critical("inst-1")
        assert len(critical) == 1 and critical[0].consumer_id == "c2"

    def test_alerts_and_incidents(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard()
        dash = svc.compute("inst-1", "c1", error_rate=0.1, avg_latency_ms=50, uptime_pct=99.99, active_alerts=3, active_incidents=1)
        assert dash.active_alerts == 3 and dash.active_incidents == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboard()
        svc.compute("inst-1", "c1", error_rate=0.1, avg_latency_ms=50, uptime_pct=99.99)
        assert svc.get("inst-2", "c1") is None
