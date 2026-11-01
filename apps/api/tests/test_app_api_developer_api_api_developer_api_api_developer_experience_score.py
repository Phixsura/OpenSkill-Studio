from app.services.app_api_developer_api_api_developer_api_api_developer_experience_score import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScore

class TestDeveloperExperienceScore:
    def test_excellent(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScore()
        dx = s.update("inst-1", doc_coverage_pct=95, onboarding_completion_pct=90, uptime_pct=99.99, avg_ticket_resolution_hours=2, nps=80)
        assert dx.dx_grade == "A"
        assert dx.dx_score >= 90

    def test_poor(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScore()
        dx = s.update("inst-1", doc_coverage_pct=20, onboarding_completion_pct=30, uptime_pct=90, avg_ticket_resolution_hours=72, nps=-50)
        assert dx.dx_score < 60

    def test_default(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScore()
        dx = s.get("inst-1")
        assert dx.doc_coverage_pct == 0.0

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScore()
        s.update("inst-1", nps=90)
        assert s.get("inst-2").nps == 0.0
