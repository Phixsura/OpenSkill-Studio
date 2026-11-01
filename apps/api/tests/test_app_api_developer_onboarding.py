"""Tests for App API Developer Onboarding — steps, progress, completion."""

import pytest
from app.services.app_api_developer_onboarding import AppAPIDeveloperOnboarding


class TestSteps:
    def test_define(self):
        o = AppAPIDeveloperOnboarding()
        steps = o.define_steps("inst-1", ["create_app", "add_webhook", "test_api"])
        assert len(steps) == 3


class TestProgress:
    def test_complete_step(self):
        o = AppAPIDeveloperOnboarding()
        o.define_steps("inst-1", ["s1", "s2", "s3"])
        p = o.complete_step("inst-1", "dev-1", "s1")
        assert p.completion_pct == 33.3

    def test_full_completion(self):
        o = AppAPIDeveloperOnboarding()
        o.define_steps("inst-1", ["s1", "s2"])
        o.complete_step("inst-1", "dev-1", "s1")
        p = o.complete_step("inst-1", "dev-1", "s2")
        assert p.is_complete is True

    def test_completion_rate(self):
        o = AppAPIDeveloperOnboarding()
        o.define_steps("inst-1", ["s1"])
        o.complete_step("inst-1", "dev-1", "s1")
        o.complete_step("inst-1", "dev-2", "s1")
        # Get dev-3 started but not complete — need 2+ steps
        o2 = AppAPIDeveloperOnboarding()
        o2.define_steps("inst-1", ["s1", "s2"])
        o2.complete_step("inst-1", "dev-1", "s1")
        o2.complete_step("inst-1", "dev-1", "s2")
        assert o2.completion_rate("inst-1") == 100.0


class TestIsolation:
    def test_cross(self):
        o = AppAPIDeveloperOnboarding()
        o.define_steps("inst-1", ["s1"])
        assert o.get_progress("inst-2", "dev-1").total_steps == 0
