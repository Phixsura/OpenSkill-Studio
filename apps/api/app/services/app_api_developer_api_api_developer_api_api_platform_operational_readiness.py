"""App API Developer Platform Operational Readiness — pre-launch readiness checklist."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ReadinessCheck:
    check_id: str
    category: str  # "security", "reliability", "monitoring", "documentation", "compliance"
    name: str
    required: bool = True
    passed: bool = False
    notes: str = ""

@dataclass
class ReadinessReport:
    checks: list[ReadinessCheck] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def required_passed(self) -> bool:
        return all(c.passed for c in self.checks if c.required)

    @property
    def readiness_pct(self) -> float:
        return round(self.passed_count / self.total * 100, 1) if self.total > 0 else 0.0

    @property
    def go_no_go(self) -> str:
        if self.required_passed and self.readiness_pct >= 90: return "GO"
        if self.required_passed: return "GO_WITH_CAVEATS"
        return "NO_GO"

class AppAPIDeveloperAPIApiDeveloperApiApiPlatformOperationalReadiness:
    def __init__(self) -> None:
        self._reports: dict[str, ReadinessReport] = {}

    def add_check(self, installation_id: str, check_id: str, category: str, name: str, required: bool = True) -> ReadinessReport:
        if not installation_id: raise ValueError("installation_id is required")
        valid_cats = {"security", "reliability", "monitoring", "documentation", "compliance"}
        if category not in valid_cats: raise ValueError("invalid category")
        r = self._reports.setdefault(installation_id, ReadinessReport())
        r.checks.append(ReadinessCheck(check_id=check_id, category=category, name=name, required=required))
        return r

    def pass_check(self, installation_id: str, check_id: str, notes: str = "") -> ReadinessReport:
        r = self._reports.get(installation_id)
        if r is None: raise KeyError("No report")
        for c in r.checks:
            if c.check_id == check_id:
                c.passed = True
                c.notes = notes
                return r
        raise KeyError(f"Check {check_id} not found")

    def get_report(self, installation_id: str) -> ReadinessReport:
        return self._reports.get(installation_id, ReadinessReport())
