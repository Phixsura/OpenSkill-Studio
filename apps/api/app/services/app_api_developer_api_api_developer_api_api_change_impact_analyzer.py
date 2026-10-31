"""App API Developer API Change Impact Analyzer — predict impact of API changes."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ImpactAssessment:
    change_id: str
    endpoint: str
    change_type: str  # "field_added", "field_removed", "type_changed", "endpoint_removed", "behavior_changed"
    affected_consumers: list[str] = field(default_factory=list)
    risk_level: str = "low"  # "low", "medium", "high", "critical"
    breaking: bool = False

    @property
    def impact_score(self) -> int:
        base = {"low": 10, "medium": 30, "high": 60, "critical": 90}.get(self.risk_level, 10)
        return min(100, base + len(self.affected_consumers) * 2)

class AppAPIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzer:
    def __init__(self) -> None:
        self._assessments: dict[tuple[str, str], ImpactAssessment] = {}

    def assess(self, installation_id: str, change_id: str, endpoint: str, change_type: str, affected_consumers: list[str], breaking: bool = False) -> ImpactAssessment:
        if not installation_id: raise ValueError("installation_id is required")
        valid_types = {"field_added", "field_removed", "type_changed", "endpoint_removed", "behavior_changed"}
        if change_type not in valid_types: raise ValueError(f"Invalid change_type: {change_type}")
        if change_type in ("field_removed", "endpoint_removed"): risk = "critical" if breaking else "high"
        elif change_type == "type_changed": risk = "high"
        elif change_type == "behavior_changed": risk = "medium"
        else: risk = "low"
        key = (installation_id, change_id)
        a = ImpactAssessment(change_id=change_id, endpoint=endpoint, change_type=change_type, affected_consumers=affected_consumers, risk_level=risk, breaking=breaking)
        self._assessments[key] = a
        return a

    def high_risk(self, installation_id: str) -> list[ImpactAssessment]:
        return [a for (inst, _), a in self._assessments.items() if inst == installation_id and a.risk_level in ("high", "critical")]

    def breaking_changes(self, installation_id: str) -> list[ImpactAssessment]:
        return [a for (inst, _), a in self._assessments.items() if inst == installation_id and a.breaking]

    def all_assessments(self, installation_id: str) -> list[ImpactAssessment]:
        return [a for (inst, _), a in self._assessments.items() if inst == installation_id]
