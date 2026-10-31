"""Log Aggregator — aggregate and analyze logs across extension instances.

Collects logs from multiple sandbox instances, provides cross-instance
search, pattern detection, and log volume analytics.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AggregatedLog:
    extension_id: str
    instance_id: str
    level: str
    message: str
    timestamp: str = ""
    tags: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class LogAggregator:
    """Aggregates logs across extension instances with analytics."""

    def __init__(self, max_logs: int = 100000):
        self._logs: list[AggregatedLog] = []
        self._max = max_logs
        self._patterns: dict[str, int] = defaultdict(int)  # message prefix -> count

    def ingest(self, log: AggregatedLog) -> None:
        self._logs.append(log)
        if len(self._logs) > self._max:
            self._logs = self._logs[-self._max:]
        # Track patterns (first 50 chars)
        key = f"{log.extension_id}:{log.level}:{log.message[:50]}"
        self._patterns[key] += 1

    def search(self, query: str, extension_id: str | None = None,
               level: str | None = None, limit: int = 100) -> list[AggregatedLog]:
        q = query.lower()
        results = self._logs
        if extension_id:
            results = [l for l in results if l.extension_id == extension_id]
        if level:
            results = [l for l in results if l.level == level]
        if query:
            results = [l for l in results if q in l.message.lower()]
        return results[-limit:]

    def get_volume(self, extension_id: str) -> dict:
        """Get log volume breakdown by level."""
        logs = [l for l in self._logs if l.extension_id == extension_id]
        by_level: dict[str, int] = defaultdict(int)
        for l in logs:
            by_level[l.level] += 1
        return {
            "extension_id": extension_id, "total": len(logs),
            "by_level": dict(by_level),
        }

    def get_frequent_patterns(self, extension_id: str, limit: int = 10) -> list[dict]:
        """Find most frequently occurring log patterns."""
        prefix = f"{extension_id}:"
        patterns = [(k.split(":", 2), v) for k, v in self._patterns.items() if k.startswith(prefix)]
        sorted_p = sorted(patterns, key=lambda x: x[1], reverse=True)[:limit]
        return [{"level": parts[1], "pattern": parts[2] if len(parts) > 2 else "", "count": count}
                for parts, count in sorted_p]

    def get_error_summary(self, extension_id: str) -> dict:
        errors = [l for l in self._logs if l.extension_id == extension_id and l.level in ("error", "critical")]
        unique = set(l.message[:80] for l in errors)
        return {
            "total_errors": len(errors),
            "unique_errors": len(unique),
            "recent": [{"message": l.message, "instance": l.instance_id, "timestamp": l.timestamp}
                       for l in errors[-5:]],
        }

    def get_instance_distribution(self, extension_id: str) -> dict[str, int]:
        """Get log count per instance."""
        dist: dict[str, int] = defaultdict(int)
        for l in self._logs:
            if l.extension_id == extension_id:
                dist[l.instance_id] += 1
        return dict(dist)
