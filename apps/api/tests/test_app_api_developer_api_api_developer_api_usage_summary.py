from app.services.app_api_developer_api_api_developer_api_usage_summary import AppAPIDeveloperAPIApiDeveloperApiUsageSummary

class TestDeveloperUsageSummary:
    def test_update(self):
        s = AppAPIDeveloperAPIApiDeveloperApiUsageSummary()
        d = s.update("inst-1", "dev1", total_requests=5000, unique_endpoints=15, avg_latency_ms=45)
        assert d.activity_level == "active"

    def test_error_rate(self):
        s = AppAPIDeveloperAPIApiDeveloperApiUsageSummary()
        d = s.update("inst-1", "dev1", total_requests=1000, error_count=50)
        assert d.error_rate_pct == 5.0

    def test_power_user(self):
        s = AppAPIDeveloperAPIApiDeveloperApiUsageSummary()
        d = s.update("inst-1", "dev1", total_requests=50000)
        assert d.activity_level == "power"

    def test_top_developers(self):
        s = AppAPIDeveloperAPIApiDeveloperApiUsageSummary()
        s.update("inst-1", "d1", total_requests=100)
        s.update("inst-1", "d2", total_requests=10000)
        top = s.top_developers("inst-1", 1)
        assert top[0].developer_id == "d2"

    def test_by_activity(self):
        s = AppAPIDeveloperAPIApiDeveloperApiUsageSummary()
        s.update("inst-1", "d1", total_requests=50000)
        s.update("inst-1", "d2", total_requests=500)
        levels = s.by_activity_level("inst-1")
        assert "power" in levels
        assert "moderate" in levels

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiUsageSummary()
        s.update("inst-1", "d1", total_requests=1000)
        assert len(s.top_developers("inst-2")) == 0
