"""Tests for App API Integration Test — create, execute, results."""

import pytest
from app.services.app_api_integration_test import AppAPIIntegrationTest

STEPS = [{"step_id": "s1", "name": "Login"}, {"step_id": "s2", "name": "Create resource"}]


class TestCreate:
    def test_create(self):
        t = AppAPIIntegrationTest()
        it = t.create("inst-1", "t1", "Auth Flow", STEPS)
        assert len(it.steps) == 2
        assert it.passed is None


class TestExecute:
    def test_all_pass(self):
        t = AppAPIIntegrationTest()
        t.create("inst-1", "t1", "Test", STEPS)
        t.start("inst-1", "t1")
        t.record_step("inst-1", "t1", "s1", True, 50)
        t.record_step("inst-1", "t1", "s2", True, 100)
        it = t.list_tests("inst-1")[0]
        assert it.passed is True
        assert it.completed_at is not None

    def test_fail(self):
        t = AppAPIIntegrationTest()
        t.create("inst-1", "t1", "Test", STEPS)
        t.record_step("inst-1", "t1", "s1", True)
        t.record_step("inst-1", "t1", "s2", False, error="404")
        it = t.list_tests("inst-1")[0]
        assert it.passed is False
        assert it.fail_count == 1


class TestIsolation:
    def test_cross(self):
        t = AppAPIIntegrationTest()
        t.create("inst-1", "t1", "Test", STEPS)
        assert t.list_tests("inst-2") == []
