"""Security Scanner — static analysis for extension code before publishing.

Scans extension source code for common security issues: dangerous imports,
hardcoded secrets, unsafe patterns, and policy violations.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    rule_id: str
    severity: Severity
    message: str
    line: int
    column: int = 0
    snippet: str = ""


DANGEROUS_IMPORTS = [
    "subprocess", "os.system", "shutil.rmtree", "ctypes",
    "importlib", "__import__", "eval", "exec",
]

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|secret|password|token)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded secret"),
    (r'(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private key in source"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Stripe test key pattern"),
    (r'ghp_[a-zA-Z0-9]{36,}', "GitHub token pattern"),
]

UNSAFE_PATTERNS = [
    (r'\beval\s*\(', "Use of eval()"),
    (r'\bexec\s*\(', "Use of exec()"),
    (r'__import__\s*\(', "Dynamic import"),
    (r'open\s*\([^)]*,\s*["\']w', "File write operation"),
    (r'requests\.get\s*\(', "Outbound HTTP request"),
]


class SecurityScanner:
    """Scans extension code for security issues."""

    def __init__(self, custom_rules: list[tuple[str, str, Severity]] | None = None):
        self._custom_rules = custom_rules or []

    def scan(self, code: str, filename: str = "extension.py") -> list[Finding]:
        """Scan code and return list of findings."""
        findings: list[Finding] = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Check dangerous imports
            for imp in DANGEROUS_IMPORTS:
                if imp in line and ("import" in line or imp in ("eval", "exec")):
                    findings.append(Finding(
                        rule_id="SEC001", severity=Severity.HIGH,
                        message=f"Dangerous import/function: {imp}",
                        line=i, snippet=line.strip(),
                    ))

            # Check hardcoded secrets
            for pattern, desc in SECRET_PATTERNS:
                if re.search(pattern, line):
                    findings.append(Finding(
                        rule_id="SEC002", severity=Severity.CRITICAL,
                        message=desc, line=i, snippet=line.strip()[:60] + "...",
                    ))

            # Check unsafe patterns
            for pattern, desc in UNSAFE_PATTERNS:
                if re.search(pattern, line):
                    findings.append(Finding(
                        rule_id="SEC003", severity=Severity.MEDIUM,
                        message=desc, line=i, snippet=line.strip(),
                    ))

            # Custom rules
            for pattern, desc, severity in self._custom_rules:
                if re.search(pattern, line):
                    findings.append(Finding(
                        rule_id="CUSTOM", severity=severity,
                        message=desc, line=i, snippet=line.strip(),
                    ))

        return findings

    def is_safe(self, code: str) -> tuple[bool, list[Finding]]:
        """Check if code passes security scan (no critical/high findings)."""
        findings = self.scan(code)
        blockers = [f for f in findings if f.severity in (Severity.CRITICAL, Severity.HIGH)]
        return len(blockers) == 0, findings

    def scan_summary(self, code: str) -> dict:
        """Get a summary of scan results."""
        findings = self.scan(code)
        by_severity = {s.value: 0 for s in Severity}
        for f in findings:
            by_severity[f.severity.value] += 1
        return {
            "total_findings": len(findings),
            "by_severity": by_severity,
            "safe": all(f.severity not in (Severity.CRITICAL, Severity.HIGH) for f in findings),
        }
