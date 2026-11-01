import pytest
from app.services.app_api_developer_api_api_developer_satisfaction_survey import AppAPIDeveloperAPIApiDeveloperSatisfactionSurvey

class TestSatisfactionSurvey:
    def test_submit(self):
        s = AppAPIDeveloperAPIApiDeveloperSatisfactionSurvey()
        r = s.submit("inst-1", "r1", "d1", 9, 5, "Great API!")
        assert r.nps_score == 9

    def test_invalid_nps(self):
        s = AppAPIDeveloperAPIApiDeveloperSatisfactionSurvey()
        with pytest.raises(ValueError):
            s.submit("inst-1", "r1", "d1", 11, 3)

    def test_nps_calculation(self):
        s = AppAPIDeveloperAPIApiDeveloperSatisfactionSurvey()
        s.submit("inst-1", "r1", "d1", 10, 5)  # promoter
        s.submit("inst-1", "r2", "d2", 9, 4)   # promoter
        s.submit("inst-1", "r3", "d3", 7, 3)   # passive
        s.submit("inst-1", "r4", "d4", 3, 1)   # detractor
        # NPS = (2 - 1) / 4 * 100 = 25.0
        assert s.nps("inst-1") == 25.0

    def test_avg_satisfaction(self):
        s = AppAPIDeveloperAPIApiDeveloperSatisfactionSurvey()
        s.submit("inst-1", "r1", "d1", 8, 5)
        s.submit("inst-1", "r2", "d2", 6, 3)
        assert s.avg_satisfaction("inst-1") == 4.0

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperSatisfactionSurvey()
        s.submit("inst-1", "r1", "d1", 9, 5)
        assert s.response_count("inst-2") == 0
