"""App API Developer OpenAPI Diff Checker — detect breaking API changes."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class APIDiff:
    diff_id: str
    change_type: str  # "breaking", "non_breaking", "deprecation"
    category: str  # "endpoint_removed", "field_removed", "type_changed", "endpoint_added", "field_added"
    path: str
    description: str

@dataclass
class DiffReport:
    from_version: str
    to_version: str
    diffs: list[APIDiff] = field(default_factory=list)

    @property
    def breaking_count(self) -> int:
        return sum(1 for d in self.diffs if d.change_type == "breaking")

    @property
    def has_breaking(self) -> bool:
        return self.breaking_count > 0

class AppAPIDeveloperAPIOpenAPIDiffChecker:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str, str], DiffReport] = {}

    def compare(self, installation_id: str, from_version: str, to_version: str, diffs: list[dict]) -> DiffReport:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, from_version, to_version)
        parsed = [APIDiff(diff_id=d["diff_id"], change_type=d["change_type"], category=d["category"], path=d["path"], description=d["description"]) for d in diffs]
        report = DiffReport(from_version=from_version, to_version=to_version, diffs=parsed)
        self._reports[key] = report
        return report

    def get_report(self, installation_id: str, from_version: str, to_version: str) -> DiffReport:
        key = (installation_id, from_version, to_version)
        r = self._reports.get(key)
        if r is None: raise KeyError(f"No diff report for {from_version} → {to_version}")
        return r

    def breaking_changes(self, installation_id: str, from_version: str, to_version: str) -> list[APIDiff]:
        r = self.get_report(installation_id, from_version, to_version)
        return [d for d in r.diffs if d.change_type == "breaking"]

    def list_reports(self, installation_id: str) -> list[DiffReport]:
        return [r for (inst, _, _), r in self._reports.items() if inst == installation_id]
