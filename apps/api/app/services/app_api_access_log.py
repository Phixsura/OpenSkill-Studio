"""App API Access Log — log API access with actor context.

Manages access logs:
- Log with actor, IP, user agent
- Filter by actor or IP
- Access pattern analysis
- Per-installation scoped logs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class AccessLogEntry:
    """An API access log entry."""

    log_id: str
    actor: str
    method: str
    path: str
    status_code: int
    ip_address: str = ""
    user_agent: str = ""
    timestamp: float = field(default_factory=time.time)


class AppAPIAccessLog:
    """Log API access with actor context."""

    def __init__(self, max_entries: int = 5000) -> None:
        self._max = max(1, max_entries)
        self._logs: dict[str, list[AccessLogEntry]] = {}

    def log(
        self, installation_id: str, log_id: str, actor: str,
        method: str, path: str, status_code: int,
        ip_address: str = "", user_agent: str = "",
    ) -> AccessLogEntry:
        if not installation_id:
            raise ValueError("installation_id is required")

        entry = AccessLogEntry(
            log_id=log_id, actor=actor, method=method.upper(),
            path=path, status_code=status_code,
            ip_address=ip_address, user_agent=user_agent,
        )
        entries = self._logs.setdefault(installation_id, [])
        entries.append(entry)
        if len(entries) > self._max:
            self._logs[installation_id] = entries[-self._max:]
        return entry

    def by_actor(self, installation_id: str, actor: str) -> list[AccessLogEntry]:
        return [e for e in self._logs.get(installation_id, []) if e.actor == actor]

    def by_ip(self, installation_id: str, ip_address: str) -> list[AccessLogEntry]:
        return [e for e in self._logs.get(installation_id, []) if e.ip_address == ip_address]

    def recent(self, installation_id: str, limit: int = 50) -> list[AccessLogEntry]:
        return list(reversed(self._logs.get(installation_id, [])[-limit:]))

    def unique_actors(self, installation_id: str) -> list[str]:
        actors: set[str] = set()
        for e in self._logs.get(installation_id, []):
            actors.add(e.actor)
        return sorted(actors)

    def count(self, installation_id: str) -> int:
        return len(self._logs.get(installation_id, []))
