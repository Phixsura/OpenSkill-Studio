"""App API Developer Breaking Change Detector — automatically detect breaking API changes."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class BreakingChange:
    change_id: str
    endpoint: str
    change_type: str  # "field_removed", "type_changed", "endpoint_removed", "required_added"
    description: str
    affected_consumers: int = 0
    severity: str = "high"

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetector:
    def __init__(self) -> None:
        self._changes: dict[tuple[str, str], BreakingChange] = {}

    def detect(self, installation_id: str, change_id: str, endpoint: str, change_type: str, description: str, affected_consumers: int = 0) -> BreakingChange:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"field_removed", "type_changed", "endpoint_removed", "required_added", "format_changed"}
        if change_type not in valid: raise ValueError(f"Invalid type: {change_type}")
        severity = "critical" if change_type == "endpoint_removed" else "high" if affected_consumers > 10 else "medium"
        key = (installation_id, change_id)
        c = BreakingChange(change_id=change_id, endpoint=endpoint, change_type=change_type, description=description, affected_consumers=affected_consumers, severity=severity)
        self._changes[key] = c
        return c

    def critical_changes(self, installation_id: str) -> list[BreakingChange]:
        return [c for (inst, _), c in self._changes.items() if inst == installation_id and c.severity == "critical"]

    def by_endpoint(self, installation_id: str, endpoint: str) -> list[BreakingChange]:
        return [c for (inst, _), c in self._changes.items() if inst == installation_id and c.endpoint == endpoint]

    def total_affected(self, installation_id: str) -> int:
        consumers: set[int] = set()  # approximate
        return sum(c.affected_consumers for (inst, _), c in self._changes.items() if inst == installation_id)

    def all_changes(self, installation_id: str) -> list[BreakingChange]:
        return [c for (inst, _), c in self._changes.items() if inst == installation_id]
