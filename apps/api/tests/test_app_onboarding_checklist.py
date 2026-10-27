"""Tests for App Onboarding Checklist — steps, completion, skip, progress, publish gate."""

import pytest

from app.services.app_onboarding_checklist import (
    AppOnboardingChecklist,
    StepStatus,
)


class TestInitialize:
    def test_creates_default_steps(self):
        c = AppOnboardingChecklist()
        steps = c.initialize("app-1")
        assert len(steps) == 9
        assert all(s.status == StepStatus.PENDING for s in steps)

    def test_steps_ordered(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        steps = c.get_steps("app-1")
        orders = [s.order for s in steps]
        assert orders == sorted(orders)

    def test_has_required_and_optional(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        steps = c.get_steps("app-1")
        assert any(s.required for s in steps)
        assert any(not s.required for s in steps)


class TestCompletion:
    def test_complete_step(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        step = c.complete_step("app-1", "manifest")
        assert step is not None
        assert step.status == StepStatus.COMPLETED
        assert step.completed_at is not None

    def test_complete_nonexistent(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        assert c.complete_step("app-1", "nonexistent") is None

    def test_complete_no_app(self):
        c = AppOnboardingChecklist()
        assert c.complete_step("app-x", "manifest") is None


class TestSkip:
    def test_skip_optional(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        step = c.skip_step("app-1", "webhook")  # optional step
        assert step is not None
        assert step.status == StepStatus.SKIPPED

    def test_skip_required_blocked(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        assert c.skip_step("app-1", "manifest") is None  # required

    def test_skip_nonexistent(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        assert c.skip_step("app-1", "nonexistent") is None


class TestReset:
    def test_reset_step(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        c.complete_step("app-1", "manifest")
        step = c.reset_step("app-1", "manifest")
        assert step.status == StepStatus.PENDING
        assert step.completed_at is None

    def test_reset_nonexistent(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        assert c.reset_step("app-1", "fake") is None


class TestProgress:
    def test_initial_progress(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        p = c.get_progress("app-1")
        assert p.total_steps == 9
        assert p.completed == 0
        assert p.pending == 9
        assert p.progress_pct == 0.0
        assert p.can_publish is False

    def test_partial_progress(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        c.complete_step("app-1", "manifest")
        c.complete_step("app-1", "permissions")
        p = c.get_progress("app-1")
        assert p.completed == 2
        assert p.progress_pct > 0

    def test_skipped_counts_in_progress(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        c.skip_step("app-1", "webhook")
        p = c.get_progress("app-1")
        assert p.skipped == 1
        assert p.progress_pct > 0

    def test_can_publish_when_all_required_done(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        steps = c.get_steps("app-1")
        for step in steps:
            if step.required:
                c.complete_step("app-1", step.step_id)
        p = c.get_progress("app-1")
        assert p.can_publish is True
        assert p.required_completed == p.required_total

    def test_cannot_publish_with_pending_required(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        c.complete_step("app-1", "manifest")
        p = c.get_progress("app-1")
        assert p.can_publish is False

    def test_empty_app_progress(self):
        c = AppOnboardingChecklist()
        p = c.get_progress("app-x")
        assert p.total_steps == 0
        assert p.progress_pct == 0.0
        assert p.can_publish is False  # fail-closed: no checklist = no publish


class TestNextStep:
    def test_next_step_is_first_pending(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        ns = c.get_next_step("app-1")
        assert ns is not None
        assert ns.order == 1

    def test_next_step_skips_completed(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        c.complete_step("app-1", "manifest")
        ns = c.get_next_step("app-1")
        assert ns.step_id != "manifest"

    def test_next_step_none_when_all_done(self):
        c = AppOnboardingChecklist()
        c.initialize("app-1")
        for step in c.get_steps("app-1"):
            if step.required:
                c.complete_step("app-1", step.step_id)
            else:
                c.skip_step("app-1", step.step_id)
        assert c.get_next_step("app-1") is None
