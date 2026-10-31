"""Error Reporting — capture, group, and analyze extension runtime errors.

Collects error reports from extensions, groups by fingerprint,
tracks occurrence counts, and provides resolution workflows.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorState(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    IGNORED = "ignored"


@dataclass
class ErrorReport:
    report_id: str
    extension_id: str
    error_type: str
    message: str
    stack_trace: str = ""
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    org_id: str = ""
    user_agent: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def fingerprint(self) -> str:
        key = f"{self.extension_id}:{self.error_type}:{self.message[:100]}"
        return hashlib.md5(key.encode()).hexdigest()[:12]


@dataclass
class ErrorGroup:
    fingerprint: str
    extension_id: str
    error_type: str
    message: str
    severity: ErrorSeverity
    state: ErrorState = ErrorState.OPEN
    count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    affected_orgs: set[str] = field(default_factory=set)


class ErrorReportingService:
    """Captures and groups extension errors for debugging."""

    def __init__(self):
        self._groups: dict[str, ErrorGroup] = {}
        self._reports: list[ErrorReport] = []

    def report(self, report: ErrorReport) -> ErrorGroup:
        """Submit an error report. Auto-groups by fingerprint."""
        fp = report.fingerprint
        self._reports.append(report)

        if fp not in self._groups:
            self._groups[fp] = ErrorGroup(
                fingerprint=fp, extension_id=report.extension_id,
                error_type=report.error_type, message=report.message,
                severity=report.severity, first_seen=report.timestamp,
            )
        group = self._groups[fp]
        group.count += 1
        group.last_seen = report.timestamp
        if report.org_id:
            group.affected_orgs.add(report.org_id)
        # Escalate severity if many occurrences
        if group.count >= 100 and group.severity != ErrorSeverity.CRITICAL:
            group.severity = ErrorSeverity.CRITICAL
        elif group.count >= 10 and group.severity == ErrorSeverity.LOW:
            group.severity = ErrorSeverity.MEDIUM
        return group

    def update_state(self, fingerprint: str, state: ErrorState) -> bool:
        group = self._groups.get(fingerprint)
        if group:
            group.state = state
            return True
        return False

    def get_groups(self, extension_id: str, state: ErrorState | None = None) -> list[ErrorGroup]:
        groups = [g for g in self._groups.values() if g.extension_id == extension_id]
        if state:
            groups = [g for g in groups if g.state == state]
        return sorted(groups, key=lambda g: g.count, reverse=True)

    def get_summary(self, extension_id: str) -> dict:
        groups = [g for g in self._groups.values() if g.extension_id == extension_id]
        return {
            "extension_id": extension_id,
            "total_groups": len(groups),
            "total_reports": sum(g.count for g in groups),
            "open": sum(1 for g in groups if g.state == ErrorState.OPEN),
            "critical": sum(1 for g in groups if g.severity == ErrorSeverity.CRITICAL),
            "unique_orgs_affected": len(set().union(*(g.affected_orgs for g in groups)) if groups else set()),
        }
