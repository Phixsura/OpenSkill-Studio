"""App API Integration Test — run integration test scenarios.

Manages integration tests:
- Define test scenarios with steps
- Execute and track pass/fail
- Record execution time
- Per-installation scoped tests
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class TestStep:
    """A step in an integration test."""

    step_id: str
    name: str
    passed: bool | None = None
    duration_ms: float = 0.0
    error: str = ""


@dataclass
class IntegrationTest:
    """An integration test scenario."""

    test_id: str
    name: str
    steps: list[TestStep] = field(default_factory=list)
    started_at: float | None = None
    completed_at: float | None = None

    @property
    def passed(self) -> bool | None:
        if any(s.passed is None for s in self.steps):
            return None
        return all(s.passed for s in self.steps)

    @property
    def pass_count(self) -> int:
        return sum(1 for s in self.steps if s.passed is True)

    @property
    def fail_count(self) -> int:
        return sum(1 for s in self.steps if s.passed is False)


class AppAPIIntegrationTest:
    """Run integration test scenarios."""

    def __init__(self) -> None:
        self._tests: dict[tuple[str, str], IntegrationTest] = {}

    def create(
        self, installation_id: str, test_id: str, name: str, steps: list[dict],
    ) -> IntegrationTest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not steps:
            raise ValueError("at least one step required")

        step_objs = [TestStep(step_id=s["step_id"], name=s["name"]) for s in steps]
        test = IntegrationTest(test_id=test_id, name=name, steps=step_objs)
        self._tests[(installation_id, test_id)] = test
        return test

    def start(self, installation_id: str, test_id: str) -> IntegrationTest:
        t = self._get(installation_id, test_id)
        t.started_at = time.time()
        return t

    def record_step(
        self, installation_id: str, test_id: str, step_id: str,
        passed: bool, duration_ms: float = 0, error: str = "",
    ) -> TestStep:
        t = self._get(installation_id, test_id)
        for s in t.steps:
            if s.step_id == step_id:
                s.passed = passed
                s.duration_ms = duration_ms
                s.error = error
                # Auto-complete if all done
                if all(st.passed is not None for st in t.steps):
                    t.completed_at = time.time()
                return s
        raise KeyError(f"Step {step_id} not found")

    def list_tests(self, installation_id: str) -> list[IntegrationTest]:
        return [t for (inst, _), t in self._tests.items() if inst == installation_id]

    def _get(self, installation_id: str, test_id: str) -> IntegrationTest:
        key = (installation_id, test_id)
        t = self._tests.get(key)
        if t is None:
            raise KeyError(f"Test {test_id} not found")
        return t
