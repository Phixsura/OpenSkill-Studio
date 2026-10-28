"""App Error Classifier — classify and group application errors.

Classifies errors for installed apps:
- Parse error messages into categories
- Group similar errors by fingerprint
- Track error frequency and first/last seen
- Per-installation scoped error groups
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
    category: str
    sample_message: str
    count: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0


class AppErrorClassifier:
    """Classify and group application errors."""

    def __init__(self) -> None:
        # (installation_id, fingerprint) → ErrorGroup
        self._groups: dict[tuple[str, str], ErrorGroup] = {}

    def classify(
        self,
        installation_id: str,
        error_type: str,
        message: str,
        stack_trace: str = "",
        now: float | None = None,
    ) -> ErrorGroup:
        """Classify an error and group it."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not error_type:
            raise ValueError("error_type is required")

        now = now or time.time()
        fingerprint = self._compute_fingerprint(error_type, message, stack_trace)
        category = self._categorize(error_type)

        key = (installation_id, fingerprint)
        group = self._groups.get(key)
        if group is None:
            group = ErrorGroup(
                fingerprint=fingerprint, category=category,
                sample_message=message, count=0,
                first_seen=now, last_seen=now,
            )
            self._groups[key] = group

        group.count += 1
        group.last_seen = now
        return group

    def get_groups(
        self,
        installation_id: str,
        category: str | None = None,
        sort_by: str = "count",
        limit: int = 50,
    ) -> list[ErrorGroup]:
        """Get error groups sorted by count or last_seen."""
        groups = [
            g for (inst, _), g in self._groups.items()
            if inst == installation_id
        ]
        if category:
            groups = [g for g in groups if g.category == category]

        if sort_by == "last_seen":
            groups.sort(key=lambda g: g.last_seen, reverse=True)
        else:
            groups.sort(key=lambda g: g.count, reverse=True)

        return groups[:limit]

    def get_category_counts(self, installation_id: str) -> dict[str, int]:
        """Count errors per category."""
        counts: dict[str, int] = {}
        for (inst, _), g in self._groups.items():
            if inst == installation_id:
                counts[g.category] = counts.get(g.category, 0) + g.count
        return counts

    def total_errors(self, installation_id: str) -> int:
        return sum(
            g.count for (inst, _), g in self._groups.items()
            if inst == installation_id
        )

    def _compute_fingerprint(self, error_type: str, message: str, stack_trace: str) -> str:
        # Use error type + first line of stack for grouping
        key = f"{error_type}:{stack_trace.split(chr(10))[0] if stack_trace else message[:100]}"
        return hashlib.sha256(key.encode()).hexdigest()[:12]

    def _categorize(self, error_type: str) -> str:
        t = error_type.lower()
        if any(k in t for k in ("timeout", "deadline", "connection")):
            return "network"
        if any(k in t for k in ("auth", "permission", "forbidden", "unauthorized")):
            return "auth"
        if any(k in t for k in ("validation", "invalid", "parse")):
            return "validation"
        if any(k in t for k in ("notfound", "404", "missing")):
            return "not_found"
        if any(k in t for k in ("rate", "throttle", "limit")):
            return "rate_limit"
        return "internal"
