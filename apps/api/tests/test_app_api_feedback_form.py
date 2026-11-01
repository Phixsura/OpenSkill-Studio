"""Tests for App API Feedback Form — submit, rating, NPS."""

import pytest
from app.services.app_api_feedback_form import AppAPIFeedbackForm


class TestSubmit:
    def test_submit(self):
        f = AppAPIFeedbackForm()
        e = f.submit("inst-1", "f1", "alice", 5, "api", "Great API!")
        assert e.rating == 5

    def test_invalid_rating(self):
        f = AppAPIFeedbackForm()
        with pytest.raises(ValueError):
            f.submit("inst-1", "f1", "alice", 6, "api")


class TestMetrics:
    def test_avg_rating(self):
        f = AppAPIFeedbackForm()
        f.submit("inst-1", "f1", "a", 5, "api")
        f.submit("inst-1", "f2", "b", 3, "api")
        assert f.avg_rating("inst-1") == 4.0

    def test_nps(self):
        f = AppAPIFeedbackForm()
        for _ in range(7):
            f.submit("inst-1", "f", "a", 5, "api")
        for _ in range(2):
            f.submit("inst-1", "f", "b", 3, "api")
        for _ in range(1):
            f.submit("inst-1", "f", "c", 1, "api")
        # promoters=7, detractors=1, total=10 → (7-1)/10*100 = 60
        assert f.nps("inst-1") == 60.0

    def test_by_category(self):
        f = AppAPIFeedbackForm()
        f.submit("inst-1", "f1", "a", 5, "api")
        f.submit("inst-1", "f2", "b", 4, "docs")
        assert f.by_category("inst-1") == {"api": 1, "docs": 1}


class TestIsolation:
    def test_cross(self):
        f = AppAPIFeedbackForm()
        f.submit("inst-1", "f1", "a", 5, "api")
        assert f.count("inst-2") == 0
