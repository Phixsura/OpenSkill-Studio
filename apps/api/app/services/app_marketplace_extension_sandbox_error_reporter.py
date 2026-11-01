"""Sandbox Error Reporter — structured error reporting with grouping.

Captures runtime errors with stack traces, groups by fingerprint,
tracks frequency, first/last seen, and generates error reports.
"""
from __future__ import annotations
import hashlib
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ErrorOccurrence:
    error_id: str
    message: str
    error_type: str
    stack_trace: str
    file: str = ""
    line: int = 0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class ErrorGroup:
    fingerprint: str
    message: str
    error_type: str
    count: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0
    resolved: bool = False
    occurrences: list[str] = field(default_factory=list)  # error_ids


class SandboxErrorReporterService:
    """Groups and tracks runtime errors by fingerprint."""

    MAX_OCCURRENCES_PER_GROUP = 100

    def __init__(self):
        self._errors: dict[str, dict[str, ErrorOccurrence]] = defaultdict(dict)
        self._groups: dict[str, dict[str, ErrorGroup]] = defaultdict(dict)

    def _fingerprint(self, error_type: str, message: str, file: str, line: int) -> str:
        raw = f"{error_type}:{message}:{file}:{line}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def report(self, sandbox_id: str, message: str, error_type: str,
               stack_trace: str = "", file: str = "",
               line: int = 0) -> ErrorOccurrence:
        error_id = f"err_{secrets.token_urlsafe(8)}"
        now = time.time()

        occurrence = ErrorOccurrence(
            error_id=error_id, message=message, error_type=error_type,
            stack_trace=stack_trace, file=file, line=line, timestamp=now,
        )
        self._errors[sandbox_id][error_id] = occurrence

        # Group by fingerprint
        fp = self._fingerprint(error_type, message, file, line)
        groups = self._groups[sandbox_id]
        if fp not in groups:
            groups[fp] = ErrorGroup(
                fingerprint=fp, message=message, error_type=error_type,
                first_seen=now,
            )
        group = groups[fp]
        group.count += 1
        group.last_seen = now
        group.resolved = False
        if len(group.occurrences) < self.MAX_OCCURRENCES_PER_GROUP:
            group.occurrences.append(error_id)

        return occurrence

    def resolve(self, sandbox_id: str, fingerprint: str) -> bool:
        group = self._groups.get(sandbox_id, {}).get(fingerprint)
        if group:
            group.resolved = True
            return True
        return False

    def get_groups(self, sandbox_id: str, unresolved_only: bool = False) -> list[ErrorGroup]:
        groups = list(self._groups.get(sandbox_id, {}).values())
        if unresolved_only:
            groups = [g for g in groups if not g.resolved]
        return sorted(groups, key=lambda g: g.last_seen, reverse=True)

    def get_top_errors(self, sandbox_id: str, limit: int = 10) -> list[ErrorGroup]:
        groups = list(self._groups.get(sandbox_id, {}).values())
        return sorted(groups, key=lambda g: g.count, reverse=True)[:limit]

    def get_error_rate(self, sandbox_id: str, window_seconds: float = 300) -> dict:
        cutoff = time.time() - window_seconds
        recent = [e for e in self._errors.get(sandbox_id, {}).values()
                  if e.timestamp >= cutoff]
        return {
            "count": len(recent),
            "window_seconds": window_seconds,
            "rate_per_minute": round(len(recent) / (window_seconds / 60), 1),
        }

    def get_stats(self, sandbox_id: str) -> dict:
        groups = self._groups.get(sandbox_id, {})
        total_errors = sum(g.count for g in groups.values())
        return {
            "total_errors": total_errors,
            "unique_errors": len(groups),
            "unresolved": sum(1 for g in groups.values() if not g.resolved),
            "resolved": sum(1 for g in groups.values() if g.resolved),
        }
