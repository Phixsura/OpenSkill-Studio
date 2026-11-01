from app.services.app_api_developer_api_developer_satisfaction import AppAPIDeveloperSatisfaction

class TestSatisfaction:
    def test_excellent(self):
        s = AppAPIDeveloperSatisfaction()
        m = s.update("inst-1", nps_score=70, csat_score=4.5, total_responses=200, promoters=150, passives=30, detractors=20)
        assert m.sentiment == "excellent"

    def test_critical(self):
        s = AppAPIDeveloperSatisfaction()
        m = s.update("inst-1", nps_score=-60)
        assert m.sentiment == "critical"

    def test_isolation(self):
        s = AppAPIDeveloperSatisfaction()
        s.update("inst-1", nps_score=50)
        assert s.get("inst-2").nps_score == 0.0
