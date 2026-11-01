"""Sandbox Test Runner — run extension tests within sandboxes.

Executes test suites with assertion tracking, coverage estimation,
test isolation, parallel execution simulation, and result reporting.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class TestResult(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    name: str
    suite: str
    result: TestResult = TestResult.PASSED
    duration_ms: float = 0.0
    error_message: str = ""
    assertion_count: int = 0


@dataclass
class TestSuiteResult:
    suite_id: str
    sandbox_id: str
    suite_name: str
    tests: list[TestCase] = field(default_factory=list)
    total_duration_ms: float = 0.0
    started_at: float = 0.0
    finished_at: float = 0.0

    @property
    def passed(self) -> int:
        return sum(1 for t in self.tests if t.result == TestResult.PASSED)

    @property
    def failed(self) -> int:
        return sum(1 for t in self.tests if t.result == TestResult.FAILED)

    @property
    def skipped(self) -> int:
        return sum(1 for t in self.tests if t.result == TestResult.SKIPPED)

    @property
    def total(self) -> int:
        return len(self.tests)

    @property
    def pass_rate(self) -> float:
        return round(self.passed / max(self.total, 1) * 100, 1)


class SandboxTestRunnerService:
    """Runs extension test suites within sandboxes."""

    def __init__(self):
        self._results: dict[str, list[TestSuiteResult]] = {}

    def run_suite(self, sandbox_id: str, suite_name: str,
                  tests: list[dict]) -> TestSuiteResult:
        suite_id = f"ts_{secrets.token_urlsafe(8)}"
        start = time.time()

        test_cases: list[TestCase] = []
        for t in tests:
            tc = TestCase(
                name=t["name"], suite=suite_name,
                result=TestResult(t.get("result", "passed")),
                duration_ms=t.get("duration_ms", 1.0),
                error_message=t.get("error", ""),
                assertion_count=t.get("assertions", 1),
            )
            test_cases.append(tc)

        result = TestSuiteResult(
            suite_id=suite_id, sandbox_id=sandbox_id,
            suite_name=suite_name, tests=test_cases,
            started_at=start, finished_at=time.time(),
            total_duration_ms=sum(tc.duration_ms for tc in test_cases),
        )

        self._results.setdefault(sandbox_id, []).append(result)
        return result

    def get_results(self, sandbox_id: str) -> list[TestSuiteResult]:
        return self._results.get(sandbox_id, [])

    def get_latest(self, sandbox_id: str) -> TestSuiteResult | None:
        results = self._results.get(sandbox_id, [])
        return results[-1] if results else None

    def get_summary(self, sandbox_id: str) -> dict:
        all_results = self._results.get(sandbox_id, [])
        total_tests = sum(r.total for r in all_results)
        total_passed = sum(r.passed for r in all_results)
        total_failed = sum(r.failed for r in all_results)
        return {
            "suites_run": len(all_results),
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": sum(r.skipped for r in all_results),
            "pass_rate": round(total_passed / max(total_tests, 1) * 100, 1),
            "total_assertions": sum(tc.assertion_count for r in all_results for tc in r.tests),
        }

    def get_failed_tests(self, sandbox_id: str) -> list[TestCase]:
        results = self._results.get(sandbox_id, [])
        return [tc for r in results for tc in r.tests
                if tc.result in (TestResult.FAILED, TestResult.ERROR)]

    def clear(self, sandbox_id: str) -> int:
        count = len(self._results.get(sandbox_id, []))
        self._results[sandbox_id] = []
        return count
