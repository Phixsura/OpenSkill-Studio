"""App Secret Scanner — detect accidentally exposed secrets in app config.

Scans configuration and code for leaked secrets:
- Pattern-based detection (API keys, tokens, passwords)
- Severity classification
- Per-installation scoped scans
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

_PATTERNS: list[tuple[str, str, str]] = [
    ("aws_key", r"AKIA[0-9A-Z]{16}", "high"),
    ("github_token", r"ghp_[A-Za-z0-9]{36}", "high"),
    ("generic_secret", r"(?i)(password|secret|api_key|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]", "medium"),
    ("private_key", r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "critical"),
    ("jwt", r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "medium"),
]


@dataclass
class SecretFinding:
    """A detected secret."""

    finding_id: str
    pattern_name: str
    severity: str
    location: str  # field name or file path
    snippet: str   # redacted snippet
    line: int = 0


@dataclass
class ScanReport:
    """Result of a secret scan."""

    installation_id: str
    findings: list[SecretFinding]
    scanned_fields: int
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0


class AppSecretScanner:
    """Detect accidentally exposed secrets."""

    def __init__(self) -> None:
        self._compiled = [(name, re.compile(pat), sev) for name, pat, sev in _PATTERNS]

    def scan_config(
        self,
        installation_id: str,
        config: dict[str, str],
    ) -> ScanReport:
        """Scan config key-value pairs for secrets."""
        if not installation_id:
            raise ValueError("installation_id is required")

        findings: list[SecretFinding] = []
        idx = 0

        for key, value in config.items():
            if not isinstance(value, str):
                continue
            for name, pattern, severity in self._compiled:
                if pattern.search(value):
                    idx += 1
                    # Redact: show first 4 chars + ***
                    match = pattern.search(value)
                    raw = match.group(0) if match else value
                    redacted = raw[:4] + "***" + raw[-2:] if len(raw) > 6 else "***"
                    findings.append(SecretFinding(
                        finding_id=f"f-{idx}",
                        pattern_name=name,
                        severity=severity,
                        location=key,
                        snippet=redacted,
                    ))

        critical = sum(1 for f in findings if f.severity == "critical")
        high = sum(1 for f in findings if f.severity == "high")
        medium = sum(1 for f in findings if f.severity == "medium")

        return ScanReport(
            installation_id=installation_id,
            findings=findings,
            scanned_fields=len(config),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
        )

    def scan_text(
        self,
        installation_id: str,
        text: str,
        location: str = "unknown",
    ) -> list[SecretFinding]:
        """Scan a block of text for secrets."""
        findings: list[SecretFinding] = []
        idx = 0
        for line_num, line in enumerate(text.split("\n"), 1):
            for name, pattern, severity in self._compiled:
                if pattern.search(line):
                    idx += 1
                    match = pattern.search(line)
                    raw = match.group(0) if match else ""
                    redacted = raw[:4] + "***" if len(raw) > 4 else "***"
                    findings.append(SecretFinding(
                        finding_id=f"f-{idx}",
                        pattern_name=name,
                        severity=severity,
                        location=location,
                        snippet=redacted,
                        line=line_num,
                    ))
        return findings
