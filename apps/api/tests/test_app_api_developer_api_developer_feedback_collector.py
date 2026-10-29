import pytest
from app.services.app_api_developer_api_developer_feedback_collector import AppAPIDeveloperAPIDeveloperFeedbackCollector

class TestFeedbackCollector:
    def test_submit(self):
        c = AppAPIDeveloperAPIDeveloperFeedbackCollector()
        f = c.submit("inst-1", "f1", "dev1", "bug", 3, "Auth is broken")
        assert f.category == "bug"

    def test_invalid_rating(self):
        c = AppAPIDeveloperAPIDeveloperFeedbackCollector()
        with pytest.raises(ValueError):
            c.submit("inst-1", "f1", "dev1", "bug", 6, "test")

    def test_avg_rating(self):
        c = AppAPIDeveloperAPIDeveloperFeedbackCollector()
        c.submit("inst-1", "f1", "d1", "bug", 5, "great")
        c.submit("inst-1", "f2", "d2", "feature", 3, "ok")
        assert c.avg_rating("inst-1") == 4.0

    def test_by_category(self):
        c = AppAPIDeveloperAPIDeveloperFeedbackCollector()
        c.submit("inst-1", "f1", "d1", "bug", 3, "x")
        c.submit("inst-1", "f2", "d2", "bug", 4, "y")
        c.submit("inst-1", "f3", "d3", "feature", 5, "z")
        assert c.by_category("inst-1") == {"bug": 2, "feature": 1}

    def test_isolation(self):
        c = AppAPIDeveloperAPIDeveloperFeedbackCollector()
        c.submit("inst-1", "f1", "d1", "bug", 3, "x")
        assert len(c.open_feedback("inst-2")) == 0
