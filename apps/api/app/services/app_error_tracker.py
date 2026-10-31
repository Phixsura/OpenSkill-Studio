"""App Error Tracker — track and group application errors.

Manages error tracking:
- Record errors with fingerprinting
- Group by fingerprint (dedup)
- Track occurrence counts
- Per-installation scoped errors
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ErrorGroup:
    """A group of similar errors."""

    fingerprint: str
    message: str
    source: str
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    count: int = 1
    resolved: bool = False


class AppErrorTracker:
    """Track and group application errors."""

    def __init__(self) -> None:
        self._groups: dict[tuple[str, str], ErrorGroup] = {}

    def record(
        self, installation_id: str, message: str, source: str,
        stack_trace: str = "",
    ) -> ErrorGroup:
        if not installation_id:
            raise ValueError("installation_id is required")

        # Fingerprint by message + source
        fp = hashlib.sha256(f"{message}:{source}".encode()).hexdigest()[:16]

        key = (installation_id, fp)
        if key in self._groups:
            group = self._groups[key]
            group.count += 1
            group.last_seen = time.time()
            if group.resolved:
                group.resolved = False  # re-open on recurrence
            return group

        group = ErrorGroup(fingerprint=fp, message=message, source=source)
        self._groups[key] = group
        return group

    def resolve(self, installation_id: str, fingerprint: str) -> ErrorGroup:
        key = (installation_id, fingerprint)
        g = self._groups.get(key)
        if g is None:
            raise KeyError(f"Error group {fingerprint} not found")
        g.resolved = True
        return g

    def unresolved(self, installation_id: str) -> list[ErrorGroup]:
        return [
            g for (inst, _), g in self._groups.items()
            if inst == installation_id and not g.resolved
        ]

    def top_errors(self, installation_id: str, limit: int = 10) -> list[ErrorGroup]:
        groups = [g for (inst, _), g in self._groups.items() if inst == installation_id]
        return sorted(groups, key=lambda g: g.count, reverse=True)[:limit]

    def count(self, installation_id: str) -> int:
        return len([g for (inst, _) in self._groups if inst == installation_id])
