"""App API Playground — interactive API request builder.

Manages API playground sessions:
- Store request templates
- Execute and record results
- History of recent requests
- Per-installation scoped playgrounds
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class PlaygroundRequest:
    """A playground API request template."""

    request_id: str
    method: str
    path: str
    headers: dict = field(default_factory=dict)
    body: str = ""
    name: str = ""


@dataclass
class PlaygroundResult:
    """Result of a playground request."""

    request_id: str
    status_code: int
    response_body: str
    duration_ms: float
    executed_at: float = field(default_factory=time.time)


class AppAPIPlayground:
    """Interactive API request builder."""

    def __init__(self, max_history: int = 100) -> None:
        self._max = max(1, max_history)
        self._templates: dict[tuple[str, str], PlaygroundRequest] = {}
        self._history: dict[str, list[PlaygroundResult]] = {}

    def save_template(
        self, installation_id: str, request_id: str, method: str, path: str,
        headers: dict | None = None, body: str = "", name: str = "",
    ) -> PlaygroundRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Invalid method: {method}")

        req = PlaygroundRequest(
            request_id=request_id, method=method.upper(), path=path,
            headers=headers or {}, body=body, name=name,
        )
        self._templates[(installation_id, request_id)] = req
        return req

    def record_result(
        self, installation_id: str, request_id: str, status_code: int,
        response_body: str, duration_ms: float,
    ) -> PlaygroundResult:
        result = PlaygroundResult(
            request_id=request_id, status_code=status_code,
            response_body=response_body, duration_ms=duration_ms,
        )
        history = self._history.setdefault(installation_id, [])
        history.append(result)
        if len(history) > self._max:
            self._history[installation_id] = history[-self._max:]
        return result

    def recent_history(self, installation_id: str, limit: int = 20) -> list[PlaygroundResult]:
        history = self._history.get(installation_id, [])
        return list(reversed(history[-limit:]))

    def list_templates(self, installation_id: str) -> list[PlaygroundRequest]:
        return [t for (inst, _), t in self._templates.items() if inst == installation_id]

    def get_template(self, installation_id: str, request_id: str) -> PlaygroundRequest:
        key = (installation_id, request_id)
        t = self._templates.get(key)
        if t is None:
            raise KeyError(f"Template {request_id} not found")
        return t
