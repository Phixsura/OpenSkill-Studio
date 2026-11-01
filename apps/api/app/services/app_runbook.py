"""App Runbook — manage operational runbooks for incident response.

Manages runbooks for installed apps:
- Create runbooks with steps
- Track runbook execution
- Link to services and incidents
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class RunbookStep:
    """A step in a runbook."""

    step_id: str
    instruction: str
    expected_outcome: str = ""


@dataclass
class Runbook:
    """An operational runbook."""

    runbook_id: str
    title: str
    description: str
    steps: list[RunbookStep]
    tags: list[str] = field(default_factory=list)
    execution_count: int = 0


class AppRunbook:
    """Manage operational runbooks."""

    def __init__(self) -> None:
        self._runbooks: dict[tuple[str, str], Runbook] = {}

    def create_runbook(
        self,
        installation_id: str,
        runbook_id: str,
        title: str,
        description: str,
        steps: list[dict],
        tags: list[str] | None = None,
    ) -> Runbook:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not runbook_id:
            raise ValueError("runbook_id is required")
        if not steps:
            raise ValueError("at least one step required")

        step_objs = [
            RunbookStep(step_id=s.get("step_id", f"s{i}"), instruction=s["instruction"],
                        expected_outcome=s.get("expected_outcome", ""))
            for i, s in enumerate(steps)
        ]

        rb = Runbook(
            runbook_id=runbook_id, title=title, description=description,
            steps=step_objs, tags=tags or [],
        )
        self._runbooks[(installation_id, runbook_id)] = rb
        return rb

    def record_execution(self, installation_id: str, runbook_id: str) -> Runbook:
        rb = self._get(installation_id, runbook_id)
        rb.execution_count += 1
        return rb

    def search(self, installation_id: str, query: str = "", tag: str = "") -> list[Runbook]:
        rbs = [r for (inst, _), r in self._runbooks.items() if inst == installation_id]
        if query:
            q = query.lower()
            rbs = [r for r in rbs if q in r.title.lower() or q in r.description.lower()]
        if tag:
            rbs = [r for r in rbs if tag in r.tags]
        return rbs

    def get_runbook(self, installation_id: str, runbook_id: str) -> Runbook:
        return self._get(installation_id, runbook_id)

    def _get(self, installation_id: str, runbook_id: str) -> Runbook:
        key = (installation_id, runbook_id)
        r = self._runbooks.get(key)
        if r is None:
            raise KeyError(f"Runbook {runbook_id} not found")
        return r
