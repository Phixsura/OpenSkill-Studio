"""Tests for Consumer Onboarding Tracker service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_onboarding_tracker import (
    OnboardingTracker, OnboardingStep,
)


class TestOnboardingTracker:
    def _setup(self):
        svc = OnboardingTracker()
        svc.define_step(OnboardingStep("s1", "Create Account", order=1))
        svc.define_step(OnboardingStep("s2", "Generate API Key", order=2))
        svc.define_step(OnboardingStep("s3", "Make First Call", order=3))
        svc.define_step(OnboardingStep("s4", "Read Docs", required=False, order=4))
        return svc

    def test_define_and_complete(self):
        svc = self._setup()
        result = svc.complete_step("c1", "s1")
        assert result["completed"] is True
        assert result["completed_count"] == 1
        assert result["progress_pct"] == 25.0

    def test_full_progress(self):
        svc = self._setup()
        for sid in ["s1", "s2", "s3"]:
            svc.complete_step("c1", sid)
        progress = svc.get_progress("c1")
        assert progress["onboarding_complete"] is True
        assert progress["required_done"] == 3

    def test_next_step(self):
        svc = self._setup()
        svc.complete_step("c1", "s1")
        nxt = svc.get_next_step("c1")
        assert nxt["step_id"] == "s2"

    def test_all_steps_done(self):
        svc = self._setup()
        for sid in ["s1", "s2", "s3", "s4"]:
            svc.complete_step("c1", sid)
        assert svc.get_next_step("c1") is None

    def test_already_completed(self):
        svc = self._setup()
        svc.complete_step("c1", "s1")
        result = svc.complete_step("c1", "s1")
        assert result["already_completed"] is True

    def test_invalid_step(self):
        svc = self._setup()
        with pytest.raises(ValueError):
            svc.complete_step("c1", "nonexistent")

    def test_completion_stats(self):
        svc = self._setup()
        for sid in ["s1", "s2", "s3"]:
            svc.complete_step("c1", sid)
        svc.complete_step("c2", "s1")
        stats = svc.get_completion_stats()
        assert stats["total_consumers"] == 2
        assert stats["fully_complete"] == 1

    def test_reset(self):
        svc = self._setup()
        svc.complete_step("c1", "s1")
        svc.reset_consumer("c1")
        progress = svc.get_progress("c1")
        assert progress["completed_count"] == 0

    def test_duplicate_step(self):
        svc = OnboardingTracker()
        svc.define_step(OnboardingStep("s1", "X"))
        with pytest.raises(ValueError):
            svc.define_step(OnboardingStep("s1", "Y"))

    def test_isolation(self):
        a = self._setup()
        b = OnboardingTracker()
        a.complete_step("c1", "s1")
        assert b.get_progress("c1")["completed_count"] == 0
