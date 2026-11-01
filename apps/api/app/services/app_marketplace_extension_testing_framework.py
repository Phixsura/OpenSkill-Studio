"""Extension Testing Framework — run automated test suites for extensions.

Provides a test runner, assertion helpers, and mock platform APIs
so extension developers can test their code before publishing.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    name: str
    status: TestStatus = TestStatus.PASSED
    duration_ms: float = 0.0
    error_message: str = ""
    assertions: int = 0


@dataclass
class TestSuite:
    suite_id: str
    extension_id: str
    name: str
    cases: list[TestCase] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""


class MockPlatformAPI:
    """Mock platform API for extension testing."""

    def __init__(self):
        self._store: dict[str, dict] = {}
        self._events: list[dict] = []

    def get(self, key: str) -> dict | None:
        return self._store.get(key)

    def set(self, key: str, value: dict) -> None:
        self._store[key] = value

    def emit(self, event_type: str, data: dict) -> None:
        self._events.append({"type": event_type, "data": data})

    def get_events(self) -> list[dict]:
        return list(self._events)

    def reset(self) -> None:
        self._store.clear()
        self._events.clear()


class ExtensionTestRunner:
    """Runs test suites for extensions with mock APIs."""

    def __init__(self):
        self._results: dict[str, TestSuite] = {}

    def create_suite(self, suite_id: str, extension_id: str, name: str) -> TestSuite:
        suite = TestSuite(
            suite_id=suite_id, extension_id=extension_id, name=name,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self._results[suite_id] = suite
        return suite

    def add_result(self, suite_id: str, case: TestCase) -> bool:
        suite = self._results.get(suite_id)
        if not suite:
            return False
        suite.cases.append(case)
        return True

    def finish_suite(self, suite_id: str) -> TestSuite | None:
        suite = self._results.get(suite_id)
        if suite:
            suite.finished_at = datetime.now(timezone.utc).isoformat()
        return suite

    def get_summary(self, suite_id: str) -> dict | None:
        suite = self._results.get(suite_id)
        if not suite:
            return None
        total = len(suite.cases)
        by_status = {s.value: 0 for s in TestStatus}
        total_duration = 0.0
        total_assertions = 0
        for c in suite.cases:
            by_status[c.status.value] += 1
            total_duration += c.duration_ms
            total_assertions += c.assertions
        return {
            "suite_id": suite_id,
            "extension_id": suite.extension_id,
            "total": total,
            "by_status": by_status,
            "total_duration_ms": round(total_duration, 2),
            "total_assertions": total_assertions,
            "pass_rate": round(by_status["passed"] / total, 4) if total > 0 else 0,
            "all_passed": by_status["failed"] == 0 and by_status["error"] == 0,
        }

    def list_suites(self, extension_id: str) -> list[TestSuite]:
        return [s for s in self._results.values() if s.extension_id == extension_id]
