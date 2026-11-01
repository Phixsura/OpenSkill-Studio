"""Crash Reporter — collect and analyze crash reports from extensions.

Captures unhandled exceptions from sandboxed extensions, deduplicates
by stack trace, tracks frequency, and provides crash-free rate metrics.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CrashReport:
    report_id: str
    extension_id: str
    version: str
    error_type: str
    message: str
    stack_trace: str
    org_id: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def fingerprint(self) -> str:
        raw = f"{self.extension_id}:{self.error_type}:{self.stack_trace[:200]}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]


@dataclass
class CrashGroup:
    fingerprint: str
    error_type: str
    message: str
    count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    versions: set[str] = field(default_factory=set)
    affected_orgs: set[str] = field(default_factory=set)
    status: str = "open"  # open, investigating, resolved, ignored


class CrashReporter:
    """Collects and analyzes extension crash reports."""

    def __init__(self):
        self._groups: dict[str, dict[str, CrashGroup]] = defaultdict(dict)  # ext -> {fp: group}
        self._total_sessions: dict[str, int] = defaultdict(int)
        self._crash_sessions: dict[str, int] = defaultdict(int)

    def record_session(self, extension_id: str) -> None:
        """Record a session start for crash-free rate calculation."""
        self._total_sessions[extension_id] += 1

    def report_crash(self, report: CrashReport) -> CrashGroup:
        """Submit a crash report. Auto-groups by fingerprint."""
        fp = report.fingerprint
        groups = self._groups[report.extension_id]
        self._crash_sessions[report.extension_id] += 1

        if fp not in groups:
            groups[fp] = CrashGroup(
                fp, report.error_type, report.message,
                first_seen=report.timestamp,
            )
        group = groups[fp]
        group.count += 1
        group.last_seen = report.timestamp
        group.versions.add(report.version)
        if report.org_id:
            group.affected_orgs.add(report.org_id)
        return group

    def get_crash_free_rate(self, extension_id: str) -> float:
        total = self._total_sessions.get(extension_id, 0)
        crashes = self._crash_sessions.get(extension_id, 0)
        if total == 0:
            return 100.0
        return round((1 - crashes / total) * 100, 2)

    def get_top_crashes(self, extension_id: str, limit: int = 10) -> list[CrashGroup]:
        groups = self._groups.get(extension_id, {})
        return sorted(groups.values(), key=lambda g: g.count, reverse=True)[:limit]

    def update_status(self, extension_id: str, fingerprint: str, status: str) -> bool:
        group = self._groups.get(extension_id, {}).get(fingerprint)
        if group:
            group.status = status
            return True
        return False

    def get_summary(self, extension_id: str) -> dict:
        groups = self._groups.get(extension_id, {})
        open_groups = [g for g in groups.values() if g.status == "open"]
        return {
            "extension_id": extension_id,
            "crash_free_rate": self.get_crash_free_rate(extension_id),
            "total_crashes": sum(g.count for g in groups.values()),
            "unique_crashes": len(groups),
            "open_issues": len(open_groups),
            "affected_versions": len(set().union(*(g.versions for g in groups.values())) if groups else set()),
        }
