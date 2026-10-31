from app.services.app_api_developer_api_api_platform_health_summary import AppAPIDeveloperAPIApiPlatformHealthSummary

class TestPlatformHealthSummary:
    def test_healthy(self):
        s = AppAPIDeveloperAPIApiPlatformHealthSummary()
        h = s.update("inst-1", api_uptime_pct=99.99, error_rate_pct=0.1, webhook_success_rate_pct=99.9)
        assert h.overall_health == "healthy"
        assert h.health_score == 100

    def test_critical(self):
        s = AppAPIDeveloperAPIApiPlatformHealthSummary()
        h = s.update("inst-1", api_uptime_pct=95.0, error_rate_pct=10.0, circuits_open=2)
        assert h.overall_health == "critical"

    def test_degraded(self):
        s = AppAPIDeveloperAPIApiPlatformHealthSummary()
        h = s.update("inst-1", api_uptime_pct=99.5, error_rate_pct=2.0)
        assert h.overall_health == "degraded"

    def test_warning(self):
        s = AppAPIDeveloperAPIApiPlatformHealthSummary()
        h = s.update("inst-1", open_findings=3)
        assert h.overall_health == "warning"

    def test_score_deductions(self):
        s = AppAPIDeveloperAPIApiPlatformHealthSummary()
        h = s.update("inst-1", api_uptime_pct=99.0, error_rate_pct=5.0, open_findings=2, avg_latency_ms=600)
        assert h.health_score < 60

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiPlatformHealthSummary()
        s.update("inst-1", api_uptime_pct=95.0)
        assert s.get("inst-2").api_uptime_pct == 100.0
