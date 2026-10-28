"""App Secret Scanner — detect leaked secrets in code and configs.

Scans text for potential secrets:
- API key patterns
- JWT tokens
- Private keys
- Connection strings
- Per-installation scoped findings
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SecretFinding:
    """A detected secret in text."""

    finding_id: str
    pattern_name: str
    matched_text: str  # redacted preview
    location: str  # file path or config key
    severity: str = "high"  # "critical", "high", "medium", "low"
    resolved: bool = False


_PATTERNS: list[tuple[str, str, re.Pattern]] = [
    ("aws_key", "high", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", "high", re.compile(r"gh[ps]_[A-Za-z0-9_]{36,}")),
    ("jwt_token", "medium", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("private_key", "critical", re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----")),
    ("generic_secret", "medium", re.compile(r"""(?:password|secret|api_key|token)\s*[=:]\s*["'][^"']{8,}["']""", re.IGNORECASE)),
    ("connection_string", "high", re.compile(r"(?:postgres|mysql|mongodb)://[^\s]{10,}")),
]


def _redact(text: str, max_show: int = 8) -> str:
    """Show first few chars then redact."""
    if len(text) <= max_show:
        return text
    return text[:max_show] + "..." + "*" * min(8, len(text) - max_show)


class AppSecretScanner:
    """Detect leaked secrets in code and configs."""

    def __init__(self) -> None:
        self._findings: dict[str, list[SecretFinding]] = {}

    def scan(
        self, installation_id: str, text: str, location: str,
        finding_id_prefix: str = "f",
    ) -> list[SecretFinding]:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not text:
            return []

        findings: list[SecretFinding] = []
        seen: set[str] = set()

        for name, severity, pattern in _PATTERNS:
            for match in pattern.finditer(text):
                matched = match.group(0)
                key = (name, matched)
                if key in seen:
                    continue
                seen.add(key)

                fid = f"{finding_id_prefix}_{name}_{len(findings)}"
                finding = SecretFinding(
                    finding_id=fid, pattern_name=name,
                    matched_text=_redact(matched),
                    location=location, severity=severity,
                )
                findings.append(finding)

        self._findings.setdefault(installation_id, []).extend(findings)
        return findings

    def resolve(self, installation_id: str, finding_id: str) -> SecretFinding:
        for f in self._findings.get(installation_id, []):
            if f.finding_id == finding_id:
                f.resolved = True
                return f
        raise KeyError(f"Finding {finding_id} not found")

    def unresolved(self, installation_id: str) -> list[SecretFinding]:
        return [f for f in self._findings.get(installation_id, []) if not f.resolved]

    def by_severity(self, installation_id: str, severity: str) -> list[SecretFinding]:
        return [f for f in self._findings.get(installation_id, []) if f.severity == severity]

    def count(self, installation_id: str) -> int:
        return len(self._findings.get(installation_id, []))
