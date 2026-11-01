"""Tests for App API Test Suite — create, execute, pass rate."""

import pytest

from app.services.app_api_test_suite import AppAPITestSuite, TestResult

TESTS = [
    {"test_id": "t1", "name": "List Users", "method": "GET", "path": "/api/v1/users", "expected_status": 200},
    {"test_id": "t2", "name": "Create User", "method": "POST", "path": "/api/v1/users", "expected_status": 201},
]


class TestCreate:
    def test_create(self):
        s = AppAPITestSuite()
        suite = s.create_suite("inst-1", "s1", "User API", TESTS)
        assert len(suite.tests) == 2

    def test_empty(self):
        s = AppAPITestSuite()
        with pytest.raises(ValueError):
            s.create_suite("inst-1", "s1", "Empty", [])


class TestExecute:
    def test_pass(self):
        s = AppAPITestSuite()
        s.create_suite("inst-1", "s1", "Suite", TESTS)
        tc = s.record_result("inst-1", "s1", "t1", 200)
        assert tc.result == TestResult.PASSED

    def test_fail(self):
        s = AppAPITestSuite()
        s.create_suite("inst-1", "s1", "Suite", TESTS)
        tc = s.record_result("inst-1", "s1", "t1", 500)
        assert tc.result == TestResult.FAILED
        assert "Expected 200" in tc.error

    def test_pass_rate(self):
        s = AppAPITestSuite()
        s.create_suite("inst-1", "s1", "Suite", TESTS)
        s.record_result("inst-1", "s1", "t1", 200)
        s.record_result("inst-1", "s1", "t2", 500)
        suite = s.get_suite("inst-1", "s1")
        assert suite.pass_rate == 50.0


class TestIsolation:
    def test_cross(self):
        s = AppAPITestSuite()
        s.create_suite("inst-1", "s1", "Suite", TESTS)
        assert s.list_suites("inst-2") == []
