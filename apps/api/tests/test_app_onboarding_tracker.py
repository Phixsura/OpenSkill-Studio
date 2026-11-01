"""Tests for App Onboarding Tracker — steps, progress, completion."""

import pytest

from app.services.app_onboarding_tracker import AppOnboardingTracker

STEPS = [
    {"step_id": "profile", "name": "Complete Profile", "required": True},
    {"step_id": "connect", "name": "Connect Account", "required": True},
    {"step_id": "tour", "name": "Take Tour", "required": False},
]


class TestDefineSteps:
    def test_define(self):
        t = AppOnboardingTracker()
        steps = t.define_steps("inst-1", STEPS)
        assert len(steps) == 3

    def test_empty(self):
        t = AppOnboardingTracker()
        with pytest.raises(ValueError):
            t.define_steps("inst-1", [])


class TestCompleteStep:
    def test_complete(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        p = t.complete_step("inst-1", "user-1", "profile")
        assert "profile" in p.completed_steps

    def test_unknown_step(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        with pytest.raises(KeyError):
            t.complete_step("inst-1", "user-1", "nope")

    def test_auto_complete(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        t.complete_step("inst-1", "user-1", "profile")
        p = t.complete_step("inst-1", "user-1", "connect")
        assert p.completed_at is not None  # all required done


class TestProgress:
    def test_progress(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        t.complete_step("inst-1", "user-1", "profile")
        prog = t.get_progress("inst-1", "user-1")
        assert prog["total_steps"] == 3
        assert prog["completed_steps"] == 1
        assert prog["completion_pct"] == pytest.approx(33.3, abs=0.1)

    def test_no_progress(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        prog = t.get_progress("inst-1", "user-1")
        assert prog["completed_steps"] == 0

    def test_step_details(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        t.complete_step("inst-1", "user-1", "profile")
        prog = t.get_progress("inst-1", "user-1")
        profile = next(s for s in prog["steps"] if s["step_id"] == "profile")
        assert profile["completed"] is True


class TestCompletionRate:
    def test_rate(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        t.complete_step("inst-1", "user-1", "profile")
        t.complete_step("inst-1", "user-1", "connect")
        t.complete_step("inst-1", "user-2", "profile")  # not complete
        assert t.get_completion_rate("inst-1") == 50.0

    def test_no_users(self):
        t = AppOnboardingTracker()
        assert t.get_completion_rate("inst-1") == 0.0


class TestIsolation:
    def test_cross_installation(self):
        t = AppOnboardingTracker()
        t.define_steps("inst-1", STEPS)
        t.complete_step("inst-1", "user-1", "profile")
        prog = t.get_progress("inst-2", "user-1")
        assert prog["total_steps"] == 0
