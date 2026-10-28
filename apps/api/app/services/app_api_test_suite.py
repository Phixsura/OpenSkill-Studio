"""App API Test Suite — manage and run API test assertions.

Manages API test suites:
- Define test cases with expected results
- Record test execution results
- Track pass/fail rates per suite
- Per-installation scoped suites
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class TestResult(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestCase:
    """An API test case."""

    test_id: str
    name: str
    method: str
    path: str
    expected_status: int
    result: TestResult = TestResult.PENDING
    actual_status: int | None = None
    error: str = ""


@dataclass
class TestSuite:
    """A collection of API test cases."""

    suite_id: str
    name: str
    tests: list[TestCase] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        executed = [t for t in self.tests if t.result in (TestResult.PASSED, TestResult.FAILED)]
        if not executed:
            return 0.0
        passed = sum(1 for t in executed if t.result == TestResult.PASSED)
        return round(passed / len(executed) * 100, 1)

    @property
    def summary(self) -> dict[str, int]:
        return {r.value: sum(1 for t in self.tests if t.result == r) for r in TestResult}


class AppAPITestSuite:
    """Manage and run API test assertions."""

    def __init__(self) -> None:
        self._suites: dict[tuple[str, str], TestSuite] = {}

    def create_suite(
        self, installation_id: str, suite_id: str, name: str,
        tests: list[dict],
    ) -> TestSuite:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not tests:
            raise ValueError("at least one test required")

        test_cases = [
            TestCase(
                test_id=t["test_id"], name=t["name"],
                method=t["method"].upper(), path=t["path"],
                expected_status=t["expected_status"],
            )
            for t in tests
        ]
        suite = TestSuite(suite_id=suite_id, name=name, tests=test_cases)
        self._suites[(installation_id, suite_id)] = suite
        return suite

    def record_result(
        self, installation_id: str, suite_id: str, test_id: str,
        actual_status: int,
    ) -> TestCase:
        suite = self._get(installation_id, suite_id)
        for tc in suite.tests:
            if tc.test_id == test_id:
                tc.actual_status = actual_status
                tc.result = TestResult.PASSED if actual_status == tc.expected_status else TestResult.FAILED
                if tc.result == TestResult.FAILED:
                    tc.error = f"Expected {tc.expected_status}, got {actual_status}"
                return tc
        raise KeyError(f"Test {test_id} not found")

    def get_suite(self, installation_id: str, suite_id: str) -> TestSuite:
        return self._get(installation_id, suite_id)

    def list_suites(self, installation_id: str) -> list[TestSuite]:
        return [s for (inst, _), s in self._suites.items() if inst == installation_id]

    def _get(self, installation_id: str, suite_id: str) -> TestSuite:
        key = (installation_id, suite_id)
        s = self._suites.get(key)
        if s is None:
            raise KeyError(f"Suite {suite_id} not found")
        return s
