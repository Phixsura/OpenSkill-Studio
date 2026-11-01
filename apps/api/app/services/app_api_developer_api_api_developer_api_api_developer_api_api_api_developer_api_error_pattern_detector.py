"""App API Developer Error Pattern Detector — detect recurring error patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorPattern:
    pattern_id: str
    error_code: str
    endpoint: str
    occurrence_count: int = 0
    first_seen_at: float = 0.0
    last_seen_at: float = 0.0
    affected_consumers: set[str] = field(default_factory=set)

    @property
    def severity(self) -> str:
        if self.occurrence_count >= 100: return "critical"
        if self.occurrence_count >= 50: return "high"
        if self.occurrence_count >= 10: return "medium"
        return "low"

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetector:
    def __init__(self) -> None:
        self._patterns: dict[tuple[str, str, str], ErrorPattern] = {}
        self._counter = 0

    def record(self, installation_id: str, error_code: str, endpoint: str, consumer_id: str, timestamp: float) -> ErrorPattern:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, error_code, endpoint)
        if key not in self._patterns:
            self._counter += 1
            self._patterns[key] = ErrorPattern(pattern_id=f"ep-{self._counter}", error_code=error_code, endpoint=endpoint, first_seen_at=timestamp)
        p = self._patterns[key]
        p.occurrence_count += 1
        p.last_seen_at = timestamp
        p.affected_consumers.add(consumer_id)
        return p

    def critical_patterns(self, installation_id: str) -> list[ErrorPattern]:
        return [p for (inst, _, _), p in self._patterns.items() if inst == installation_id and p.severity == "critical"]

    def top_patterns(self, installation_id: str, limit: int = 10) -> list[ErrorPattern]:
        patterns = [p for (inst, _, _), p in self._patterns.items() if inst == installation_id]
        return sorted(patterns, key=lambda p: p.occurrence_count, reverse=True)[:limit]

    def by_endpoint(self, installation_id: str, endpoint: str) -> list[ErrorPattern]:
        return [p for (inst, _, _), p in self._patterns.items() if inst == installation_id and p.endpoint == endpoint]
