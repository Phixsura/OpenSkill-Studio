"""App Playground Runner — execute API requests in a sandboxed playground.

Manages interactive API playground sessions:
- Execute API calls with request/response capture
- Save and replay request history
- Per-installation scoped playgrounds
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class PlaygroundRequest:
    """A playground API request."""

    request_id: str
    method: str
    path: str
    headers: dict = field(default_factory=dict)
    body: str = ""
    query_params: dict = field(default_factory=dict)


@dataclass
class PlaygroundResponse:
    """A playground API response."""

    status_code: int
    headers: dict = field(default_factory=dict)
    body: str = ""
    duration_ms: float = 0.0


@dataclass
class PlaygroundExecution:
    """A complete request/response execution."""

    execution_id: str
    installation_id: str
    request: PlaygroundRequest
    response: PlaygroundResponse | None = None
    timestamp: float = field(default_factory=time.time)
    saved: bool = False
    name: str = ""


class AppPlaygroundRunner:
    """Execute API requests in a sandboxed playground."""

    def __init__(self, max_history: int = 100) -> None:
        self._executions: dict[tuple[str, str], PlaygroundExecution] = {}
        self._history: dict[str, list[str]] = {}  # installation_id → execution_ids
        self._max_history = max(1, max_history)

    def execute(
        self,
        installation_id: str,
        execution_id: str,
        request: PlaygroundRequest,
        response: PlaygroundResponse,
        name: str = "",
        now: float | None = None,
    ) -> PlaygroundExecution:
        """Record a playground execution."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not execution_id:
            raise ValueError("execution_id is required")

        key = (installation_id, execution_id)
        if key in self._executions:
            raise ValueError(f"Execution {execution_id} already exists")

        execution = PlaygroundExecution(
            execution_id=execution_id,
            installation_id=installation_id,
            request=request,
            response=response,
            timestamp=now or time.time(),
            name=name,
        )
        self._executions[key] = execution

        history = self._history.setdefault(installation_id, [])
        history.append(execution_id)
        if len(history) > self._max_history:
            old_id = history.pop(0)
            self._executions.pop((installation_id, old_id), None)

        return execution

    def save_execution(self, installation_id: str, execution_id: str, name: str = "") -> PlaygroundExecution:
        """Mark an execution as saved (bookmarked)."""
        e = self._get(installation_id, execution_id)
        e.saved = True
        if name:
            e.name = name
        return e

    def get_execution(self, installation_id: str, execution_id: str) -> PlaygroundExecution:
        return self._get(installation_id, execution_id)

    def get_history(self, installation_id: str, saved_only: bool = False, limit: int = 20) -> list[PlaygroundExecution]:
        """Get execution history, newest first."""
        ids = self._history.get(installation_id, [])
        executions = []
        for eid in reversed(ids):
            e = self._executions.get((installation_id, eid))
            if e and (not saved_only or e.saved):
                executions.append(e)
            if len(executions) >= limit:
                break
        return executions

    def _get(self, installation_id: str, execution_id: str) -> PlaygroundExecution:
        key = (installation_id, execution_id)
        e = self._executions.get(key)
        if e is None:
            raise KeyError(f"Execution {execution_id} not found")
        return e
