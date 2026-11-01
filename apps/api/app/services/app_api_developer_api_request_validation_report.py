"""App API Developer Request Validation Report — track request validation failures."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ValidationFailure:
    endpoint: str
    field: str
    rule: str  # "required", "type", "format", "range", "pattern"
    value_preview: str = ""
    count: int = 1

class AppAPIDeveloperAPIRequestValidationReport:
    def __init__(self) -> None:
        self._failures: dict[str, dict[tuple[str, str, str], ValidationFailure]] = {}

    def record(self, installation_id: str, endpoint: str, field: str, rule: str, value_preview: str = "") -> ValidationFailure:
        if not installation_id: raise ValueError("installation_id is required")
        if rule not in ("required", "type", "format", "range", "pattern"): raise ValueError("invalid rule")
        bucket = self._failures.setdefault(installation_id, {})
        key = (endpoint, field, rule)
        if key in bucket:
            bucket[key].count += 1
        else:
            bucket[key] = ValidationFailure(endpoint=endpoint, field=field, rule=rule, value_preview=value_preview)
        return bucket[key]

    def top_failures(self, installation_id: str, limit: int = 10) -> list[ValidationFailure]:
        bucket = self._failures.get(installation_id, {})
        return sorted(bucket.values(), key=lambda f: f.count, reverse=True)[:limit]

    def by_endpoint(self, installation_id: str, endpoint: str) -> list[ValidationFailure]:
        bucket = self._failures.get(installation_id, {})
        return [f for f in bucket.values() if f.endpoint == endpoint]

    def total_failures(self, installation_id: str) -> int:
        return sum(f.count for f in self._failures.get(installation_id, {}).values())

    def by_rule(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self._failures.get(installation_id, {}).values():
            counts[f.rule] = counts.get(f.rule, 0) + f.count
        return counts
