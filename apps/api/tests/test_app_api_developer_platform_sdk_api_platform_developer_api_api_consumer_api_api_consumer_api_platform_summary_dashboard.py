import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_platform_summary_dashboard import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard, PlatformSummary, PlatformMetric,
)

class TestPlatformSummaryDashboard:
    def test_update_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard()
        svc.update("inst-1", PlatformSummary(total_consumers=50, active_consumers=45, total_api_keys=120, health_score=95, metrics=[PlatformMetric(name="Revenue", value=25000, unit="USD")]))
        got = svc.get("inst-1")
        assert got.total_consumers == 50 and got.health_score == 95

    def test_default_empty(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard()
        assert svc.get("missing").total_consumers == 0

    def test_compute_health_good(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard()
        assert svc.compute_health(error_rate=0.1, avg_latency_ms=50, uptime_pct=99.99) > 90

    def test_compute_health_degraded(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard()
        assert svc.compute_health(error_rate=5, avg_latency_ms=500, uptime_pct=98) < 80

    def test_invalid_health(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard()
        with pytest.raises(ValueError, match="health_score"):
            svc.update("inst-1", PlatformSummary(health_score=150))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiPlatformSummaryDashboard()
        svc.update("inst-1", PlatformSummary(total_consumers=10))
        assert svc.get("inst-2").total_consumers == 0
