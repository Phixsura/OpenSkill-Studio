from app.services.app_api_developer_api_api_platform_analytics_summary import AppAPIDeveloperAPIApiPlatformAnalyticsSummary

class TestAnalyticsSummary:
    def test_excellent(self):
        s = AppAPIDeveloperAPIApiPlatformAnalyticsSummary()
        a = s.update("inst-1", error_rate_pct=0.05, p99_latency_ms=200)
        assert a.health_indicator == "excellent"

    def test_poor(self):
        s = AppAPIDeveloperAPIApiPlatformAnalyticsSummary()
        a = s.update("inst-1", error_rate_pct=10, p99_latency_ms=3000)
        assert a.health_indicator == "poor"

    def test_full_update(self):
        s = AppAPIDeveloperAPIApiPlatformAnalyticsSummary()
        a = s.update("inst-1", total_requests_7d=500000, unique_consumers_7d=200, avg_latency_ms=45, top_endpoint="/api/users", request_growth_pct=15.5)
        assert a.total_requests_7d == 500000
        assert a.request_growth_pct == 15.5

    def test_default(self):
        s = AppAPIDeveloperAPIApiPlatformAnalyticsSummary()
        a = s.get("inst-1")
        assert a.total_requests_7d == 0
        assert a.health_indicator == "excellent"

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiPlatformAnalyticsSummary()
        s.update("inst-1", total_requests_7d=100000)
        assert s.get("inst-2").total_requests_7d == 0
