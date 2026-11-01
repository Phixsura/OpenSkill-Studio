"""Tests for App Analytics Funnel — steps, progress, conversion, drop-off."""

import pytest

from app.services.app_analytics_funnel import AppAnalyticsFunnel

STEPS = [
    {"step_id": "visit", "name": "Visit Page"},
    {"step_id": "signup", "name": "Sign Up"},
    {"step_id": "activate", "name": "Activate"},
    {"step_id": "purchase", "name": "Purchase"},
]


class TestCreateFunnel:
    def test_create(self):
        f = AppAnalyticsFunnel()
        funnel = f.create_funnel("inst-1", "onboarding", "Onboarding", STEPS)
        assert funnel.funnel_id == "onboarding"
        assert len(funnel.steps) == 4

    def test_too_few_steps(self):
        f = AppAnalyticsFunnel()
        with pytest.raises(ValueError, match="2 steps"):
            f.create_funnel("inst-1", "f1", "X", [{"step_id": "a", "name": "A"}])

    def test_duplicate(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        with pytest.raises(ValueError, match="already exists"):
            f.create_funnel("inst-1", "f1", "Y", STEPS)


class TestRecordStep:
    def test_record(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        f.record_step("inst-1", "f1", "visit", "user-1")
        metrics = f.get_metrics("inst-1", "f1")
        assert metrics[0].entered == 1

    def test_unknown_funnel(self):
        f = AppAnalyticsFunnel()
        with pytest.raises(KeyError):
            f.record_step("inst-1", "nope", "visit", "user-1")

    def test_dedup_user(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        f.record_step("inst-1", "f1", "visit", "user-1")
        f.record_step("inst-1", "f1", "visit", "user-1")
        metrics = f.get_metrics("inst-1", "f1")
        assert metrics[0].entered == 1


class TestMetrics:
    def test_conversion_rates(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        for uid in ["u1", "u2", "u3", "u4", "u5"]:
            f.record_step("inst-1", "f1", "visit", uid)
        for uid in ["u1", "u2", "u3"]:
            f.record_step("inst-1", "f1", "signup", uid)
        for uid in ["u1", "u2"]:
            f.record_step("inst-1", "f1", "activate", uid)
        f.record_step("inst-1", "f1", "purchase", "u1")

        metrics = f.get_metrics("inst-1", "f1")
        assert metrics[0].entered == 5
        assert metrics[1].entered == 3
        assert metrics[1].conversion_pct == 60.0
        assert metrics[1].drop_off_pct == 40.0
        assert metrics[3].entered == 1

    def test_empty_funnel(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        metrics = f.get_metrics("inst-1", "f1")
        assert all(m.entered == 0 for m in metrics)


class TestOverallConversion:
    def test_overall(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        for uid in ["u1", "u2", "u3", "u4"]:
            f.record_step("inst-1", "f1", "visit", uid)
        f.record_step("inst-1", "f1", "purchase", "u1")
        assert f.get_overall_conversion("inst-1", "f1") == 25.0

    def test_zero_when_empty(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        assert f.get_overall_conversion("inst-1", "f1") == 0.0


class TestIsolation:
    def test_cross_installation(self):
        f = AppAnalyticsFunnel()
        f.create_funnel("inst-1", "f1", "X", STEPS)
        with pytest.raises(KeyError):
            f.get_funnel("inst-2", "f1")
