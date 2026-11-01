"""App API Developer Webhook Security Scanner — scan webhook configs for security issues."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class SecurityFinding:
    finding_id: str
    severity: str  # "critical", "high", "medium", "low"
    category: str
    message: str
    destination: str

class AppAPIDeveloperAPIApiWebhookSecurityScanner:
    def __init__(self) -> None:
        self._findings: dict[str, list[SecurityFinding]] = {}
        self._counter = 0

    def scan(self, installation_id: str, destination: str, secret: str | None = None, uses_https: bool = True, signature_algorithm: str = "") -> list[SecurityFinding]:
        if not installation_id: raise ValueError("installation_id is required")
        findings: list[SecurityFinding] = []
        if not uses_https:
            findings.append(self._make(installation_id, "critical", "transport", "Webhook uses HTTP instead of HTTPS", destination))
        if not secret:
            findings.append(self._make(installation_id, "high", "auth", "No webhook secret configured", destination))
        elif len(secret) < 32:
            findings.append(self._make(installation_id, "medium", "auth", "Webhook secret is too short (< 32 chars)", destination))
        if signature_algorithm == "sha1":
            findings.append(self._make(installation_id, "medium", "crypto", "Using SHA-1 instead of SHA-256", destination))
        if not signature_algorithm and secret:
            findings.append(self._make(installation_id, "low", "config", "No signature algorithm specified", destination))
        self._findings.setdefault(installation_id, []).extend(findings)
        return findings

    def all_findings(self, installation_id: str) -> list[SecurityFinding]:
        return self._findings.get(installation_id, [])

    def critical_count(self, installation_id: str) -> int:
        return sum(1 for f in self._findings.get(installation_id, []) if f.severity == "critical")

    def by_severity(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self._findings.get(installation_id, []):
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _make(self, installation_id: str, severity: str, category: str, message: str, destination: str) -> SecurityFinding:
        self._counter += 1
        return SecurityFinding(finding_id=f"sf-{self._counter}", severity=severity, category=category, message=message, destination=destination)
