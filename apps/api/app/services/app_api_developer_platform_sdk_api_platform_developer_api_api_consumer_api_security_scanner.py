"""API Consumer Security Scanner — scan consumer integrations for security issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import structlog

log = structlog.get_logger()

class ScanSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityFinding:
    finding_id: str
    category: str  # "auth", "encryption", "headers", "rate_limit", "data_exposure"
    severity: ScanSeverity
    title: str
    description: str = ""
    remediation: str = ""
    resolved: bool = False

@dataclass
class ScanResult:
    scan_id: str
    consumer_id: str
    findings: list[SecurityFinding] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == ScanSeverity.CRITICAL and not f.resolved)

    @property
    def score(self) -> int:
        penalties = {ScanSeverity.CRITICAL: 25, ScanSeverity.HIGH: 15, ScanSeverity.MEDIUM: 5, ScanSeverity.LOW: 2}
        total_penalty = sum(penalties.get(f.severity, 0) for f in self.findings if not f.resolved)
        return max(0, 100 - total_penalty)

VALID_CATEGORIES = {"auth", "encryption", "headers", "rate_limit", "data_exposure", "injection", "cors"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSecurityScanner:
    def __init__(self) -> None:
        self._scans: dict[tuple[str, str], ScanResult] = {}

    def run_scan(self, installation_id: str, scan_id: str, consumer_id: str, findings: list[SecurityFinding]) -> ScanResult:
        if not installation_id: raise ValueError("installation_id is required")
        for f in findings:
            if f.category not in VALID_CATEGORIES: raise ValueError(f"Invalid category: {f.category}")
        result = ScanResult(scan_id=scan_id, consumer_id=consumer_id, findings=findings)
        self._scans[(installation_id, consumer_id)] = result
        return result

    def resolve_finding(self, installation_id: str, consumer_id: str, finding_id: str) -> SecurityFinding:
        scan = self._scans.get((installation_id, consumer_id))
        if scan is None: raise KeyError(f"No scan for {consumer_id}")
        for f in scan.findings:
            if f.finding_id == finding_id: f.resolved = True; return f
        raise KeyError(f"Finding {finding_id} not found")

    def get_score(self, installation_id: str, consumer_id: str) -> int:
        scan = self._scans.get((installation_id, consumer_id))
        return scan.score if scan else 100

    def consumers_at_risk(self, installation_id: str, threshold: int = 70) -> list[str]:
        return [cid for (inst, cid), s in self._scans.items() if inst == installation_id and s.score < threshold]

    def list_scans(self, installation_id: str) -> list[ScanResult]:
        return [s for (inst, _), s in self._scans.items() if inst == installation_id]
