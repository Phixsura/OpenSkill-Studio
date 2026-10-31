from app.services.app_api_developer_platform_summary import AppAPIDeveloperPlatformSummary

class TestSummary:
    def test_update(self):
        s = AppAPIDeveloperPlatformSummary()
        ps = s.update("inst-1", total_developers=200, total_api_calls_30d=1000000, webhook_success_rate=99.5)
        assert ps.total_developers == 200

    def test_grade_a(self):
        s = AppAPIDeveloperPlatformSummary()
        s.update("inst-1", api_error_rate=0.5, webhook_success_rate=99.9, open_incidents=0, documentation_coverage_pct=95)
        assert s.health_grade("inst-1") == "A"

    def test_grade_d(self):
        s = AppAPIDeveloperPlatformSummary()
        s.update("inst-1", api_error_rate=10, webhook_success_rate=80, open_incidents=5, documentation_coverage_pct=30)
        assert s.health_grade("inst-1") == "D"

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSummary()
        s.update("inst-1", total_developers=100)
        assert s.get("inst-2").total_developers == 0
