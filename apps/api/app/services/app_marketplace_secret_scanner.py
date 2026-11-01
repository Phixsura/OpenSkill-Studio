"""Secret Scanner — detect leaked secrets in extension source before publish.

Scans code for common secret patterns (API keys, tokens, passwords)
and blocks publishing if any are found. Complements the security scanner
with specialized secret detection.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class SecretFinding:
    rule_id: str
    description: str
    line: int
    matched_pattern: str
    severity: str = "high"
    redacted_match: str = ""


# Patterns use generic forms to avoid triggering GitHub's own scanner
SECRET_RULES = [
    ("SEC-S01", "Generic API key assignment", r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][a-zA-Z0-9]{16,}["\']'),
    ("SEC-S02", "Generic secret/password assignment", r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*["\'][^\s"\']{8,}["\']'),
    ("SEC-S03", "Generic token assignment", r'(?i)(token|auth[_-]?token|access[_-]?token)\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}["\']'),
    ("SEC-S04", "Private key header", r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'),
    ("SEC-S05", "Database connection string", r'(?i)(postgres|mysql|mongodb)://\w+:[^@\s]+@'),
    ("SEC-S06", "AWS-style key ID", r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{12,}'),
    ("SEC-S07", "Hardcoded IP with port", r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b'),
]

ALLOWLIST_PATTERNS = [
    r'example\.com',
    r'localhost',
    r'127\.0\.0\.1',
    r'0\.0\.0\.0',
    r'placeholder',
    r'your[_-]',
    r'<[A-Z_]+>',
    r'TODO',
]


class SecretScanner:
    """Scans extension source code for leaked secrets."""

    def __init__(self, extra_rules: list[tuple[str, str, str]] | None = None):
        self._rules = list(SECRET_RULES)
        if extra_rules:
            self._rules.extend(extra_rules)

    def _is_allowlisted(self, line: str) -> bool:
        for pattern in ALLOWLIST_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def _redact(self, match: str) -> str:
        if len(match) <= 8:
            return "***"
        return match[:4] + "***" + match[-4:]

    def scan(self, code: str) -> list[SecretFinding]:
        findings = []
        for i, line in enumerate(code.split("\n"), 1):
            if self._is_allowlisted(line):
                continue
            for rule_id, desc, pattern in self._rules:
                m = re.search(pattern, line)
                if m:
                    findings.append(SecretFinding(
                        rule_id=rule_id, description=desc, line=i,
                        matched_pattern=pattern,
                        redacted_match=self._redact(m.group()),
                    ))
        return findings

    def scan_safe(self, code: str) -> tuple[bool, list[SecretFinding]]:
        """Returns (is_safe, findings). Safe means no secrets detected."""
        findings = self.scan(code)
        return len(findings) == 0, findings

    def get_rules(self) -> list[dict]:
        return [{"id": r[0], "description": r[1]} for r in self._rules]
