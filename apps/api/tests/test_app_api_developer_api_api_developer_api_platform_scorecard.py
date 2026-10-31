from app.services.app_api_developer_api_api_developer_api_platform_scorecard import AppAPIDeveloperAPIApiDeveloperApiPlatformScorecard

class TestPlatformScorecard:
    def test_perfect_score(self):
        s = AppAPIDeveloperAPIApiDeveloperApiPlatformScorecard()
        sc = s.update("inst-1", uptime_pct=99.99, error_rate_pct=0.01, avg_latency_ms=45, p99_latency_ms=200, cache_hit_rate_pct=95, security_score=100)
        assert sc.overall_grade == "A"
        assert sc.reliability_score >= 99

    def test_poor_reliability(self):
        s = AppAPIDeveloperAPIApiDeveloperApiPlatformScorecard()
        sc = s.update("inst-1", uptime_pct=90, error_rate_pct=10)
        assert sc.reliability_score < 90

    def test_security_grade_with_overdue(self):
        s = AppAPIDeveloperAPIApiDeveloperApiPlatformScorecard()
        sc = s.update("inst-1", security_score=95, secret_rotation_overdue=2)
        assert sc.security_grade == "B"

    def test_default(self):
        s = AppAPIDeveloperAPIApiDeveloperApiPlatformScorecard()
        sc = s.get("inst-1")
        assert sc.total_services == 483
        assert sc.overall_grade == "A"

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiPlatformScorecard()
        s.update("inst-1", active_developers=500)
        assert s.get("inst-2").active_developers == 0
