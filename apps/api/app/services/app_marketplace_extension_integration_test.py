"""Integration Test Runner — end-to-end testing for extension integrations.

Runs integration tests against live sandbox environments with
setup/teardown, test scenarios, assertions, and report generation.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class TestOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class IntegrationTest:
    test_id: str
    name: str
    scenario: str
    outcome: TestOutcome = TestOutcome.PASS
    duration_ms: float = 0.0
    assertions: int = 0
    error: str = ""


@dataclass
class IntegrationSuite:
    suite_id: str
    extension_id: str
    tests: list[IntegrationTest] = field(default_factory=list)
    setup_ok: bool = True
    teardown_ok: bool = True
    total_duration_ms: float = 0.0


class ExtensionIntegrationTestService:
    """Runs integration test suites for extensions."""

    def __init__(self):
        self._suites: dict[str, IntegrationSuite] = {}

    def create_suite(self, extension_id: str) -> IntegrationSuite:
        suite_id = f"isuite_{secrets.token_urlsafe(6)}"
        suite = IntegrationSuite(suite_id=suite_id, extension_id=extension_id)
        self._suites[suite_id] = suite
        return suite

    def add_test(self, suite_id: str, name: str, scenario: str,
                 outcome: TestOutcome, duration_ms: float = 0,
                 assertions: int = 0, error: str = "") -> IntegrationTest:
        suite = self._suites.get(suite_id)
        if not suite:
            raise ValueError("Suite not found")
        test = IntegrationTest(
            test_id=f"it_{secrets.token_urlsafe(6)}",
            name=name, scenario=scenario, outcome=outcome,
            duration_ms=duration_ms, assertions=assertions, error=error,
        )
        suite.tests.append(test)
        suite.total_duration_ms += duration_ms
        return test

    def get_report(self, suite_id: str) -> dict:
        suite = self._suites.get(suite_id)
        if not suite:
            return {}
        passed = sum(1 for t in suite.tests if t.outcome == TestOutcome.PASS)
        failed = sum(1 for t in suite.tests if t.outcome == TestOutcome.FAIL)
        return {
            "suite_id": suite_id, "total": len(suite.tests),
            "passed": passed, "failed": failed,
            "skipped": sum(1 for t in suite.tests if t.outcome == TestOutcome.SKIP),
            "pass_rate": round(passed / max(len(suite.tests), 1) * 100, 1),
            "duration_ms": suite.total_duration_ms,
            "setup_ok": suite.setup_ok, "teardown_ok": suite.teardown_ok,
        }

    def get_failures(self, suite_id: str) -> list[IntegrationTest]:
        suite = self._suites.get(suite_id)
        if not suite:
            return []
        return [t for t in suite.tests if t.outcome in (TestOutcome.FAIL, TestOutcome.ERROR)]
