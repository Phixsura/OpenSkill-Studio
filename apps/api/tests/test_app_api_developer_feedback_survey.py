import pytest
from app.services.app_api_developer_feedback_survey import AppAPIDeveloperFeedbackSurvey

class TestSurvey:
    def test_create(self):
        s = AppAPIDeveloperFeedbackSurvey()
        survey = s.create("inst-1", "s1", "API Satisfaction", ["How easy?", "What to improve?"])
        assert len(survey.questions) == 2

    def test_submit(self):
        s = AppAPIDeveloperFeedbackSurvey()
        s.create("inst-1", "s1", "Survey", ["Q1"])
        survey = s.submit_response("inst-1", "s1", "alice", {"Q1": "Great"})
        assert survey.response_count == 1

    def test_no_questions(self):
        s = AppAPIDeveloperFeedbackSurvey()
        with pytest.raises(ValueError):
            s.create("inst-1", "s1", "Empty", [])

    def test_isolation(self):
        s = AppAPIDeveloperFeedbackSurvey()
        s.create("inst-1", "s1", "S", ["Q"])
        assert s.list_surveys("inst-2") == []
