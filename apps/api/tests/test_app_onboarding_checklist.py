"""Tests for App Onboarding Checklist — steps, progress, completion."""

import pytest

from app.services.app_onboarding_checklist import AppOnboardingChecklist


class TestSteps:
    def test_add(self):
        o = AppOnboardingChecklist()
        s = o.add_step("inst-1", "s1", "Create App", "Register your first app")
        assert s.required is True


class TestProgress:
    def test_complete_step(self):
        o = AppOnboardingChecklist()
        o.add_step("inst-1", "s1", "Create App", "Desc")
        o.add_step("inst-1", "s2", "Add Webhook", "Desc")
        o.complete_step("inst-1", "user-1", "s1")
        assert o.completion_pct("inst-1", "user-1") == 50.0

    def test_full_completion(self):
        o = AppOnboardingChecklist()
        o.add_step("inst-1", "s1", "Step 1", "Desc")
        o.add_step("inst-1", "s2", "Step 2", "Desc")
        o.complete_step("inst-1", "user-1", "s1")
        o.complete_step("inst-1", "user-1", "s2")
        assert o.is_complete("inst-1", "user-1") is True

    def test_remaining(self):
        o = AppOnboardingChecklist()
        o.add_step("inst-1", "s1", "Step 1", "Desc")
        o.add_step("inst-1", "s2", "Step 2", "Desc")
        o.complete_step("inst-1", "user-1", "s1")
        remaining = o.remaining_steps("inst-1", "user-1")
        assert len(remaining) == 1
        assert remaining[0].step_id == "s2"

    def test_optional_ignored(self):
        o = AppOnboardingChecklist()
        o.add_step("inst-1", "s1", "Required", "Desc", required=True)
        o.add_step("inst-1", "s2", "Optional", "Desc", required=False)
        o.complete_step("inst-1", "user-1", "s1")
        assert o.is_complete("inst-1", "user-1") is True


class TestIsolation:
    def test_cross(self):
        o = AppOnboardingChecklist()
        o.add_step("inst-1", "s1", "Step", "Desc")
        o.complete_step("inst-1", "user-1", "s1")
        assert o.completion_pct("inst-2", "user-1") == 100.0  # no steps = 100%
