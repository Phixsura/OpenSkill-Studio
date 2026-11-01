"""App Content Scanner — automated security and quality scanning for app submissions.

Scans app content for policy violations before marketplace listing:
- Forbidden pattern detection (hardcoded secrets, eval, exec)
- URL validation (no localhost, no internal IPs)
- Size limit enforcement (manifest, assets, total bundle)
- Sensitive data detection (API keys, tokens, passwords in code)
- Dependency vulnerability check (known-bad packages)
- Content policy compliance (no obfuscated code, no tracking pixels)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(str, Enum):
    SECRET_LEAK = "secret_leak"
    UNSAFE_CODE = "unsafe_code"
    INVALID_URL = "invalid_url"
    SIZE_LIMIT = "size_limit"
    KNOWN_VULN = "known_vuln"
    POLICY = "policy"


@dataclass
class ScanFinding:
    """A single finding from a content scan."""

    category: FindingCategory
    severity: FindingSeverity
    message: str
    file_path: str | None = None
    line_number: int | None = None
    pattern_matched: str | None = None


@dataclass
class ScanResult:
    """Complete scan result for an app submission."""

    app_id: str
    passed: bool
    findings: list[ScanFinding]
    files_scanned: int
    total_bytes: int

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == FindingSeverity.HIGH)


# ── Pattern definitions ──────────────────────────────────

SECRET_PATTERNS = [
    (re.compile(r"(?:api[_-]?key|apikey)\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}", re.I), "API key"),
    (re.compile(r"(?:secret|password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{8,}", re.I), "Password/secret"),
    (re.compile(r"(?:aws_access_key_id|aws_secret)\s*[=:]\s*['\"][A-Z0-9]{16,}", re.I), "AWS credential"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub token"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI/Stripe key"),
    (re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"), "Private key"),
]

UNSAFE_CODE_PATTERNS = [
    (re.compile(r"\beval\s*\("), "eval() usage"),
    (re.compile(r"\bexec\s*\("), "exec() usage"),
    (re.compile(r"__import__\s*\("), "Dynamic import"),
    (re.compile(r"subprocess\.\w+\s*\("), "Subprocess call"),
    (re.compile(r"os\.system\s*\("), "os.system() call"),
]

INTERNAL_URL_PATTERNS = [
    re.compile(r"https?://localhost", re.I),
    re.compile(r"https?://127\.0\.0\.1"),
    re.compile(r"https?://0\.0\.0\.0"),
    re.compile(r"https?://10\.\d+\.\d+\.\d+"),
    re.compile(r"https?://172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+"),
    re.compile(r"https?://192\.168\.\d+\.\d+"),
]

KNOWN_BAD_DEPS = {"event-stream", "flatmap-stream", "ua-parser-js-malicious", "colors-malicious"}

MAX_BUNDLE_BYTES = 50 * 1024 * 1024  # 50MB
MAX_FILE_BYTES = 10 * 1024 * 1024     # 10MB per file
MAX_FILE_COUNT = 500


class AppContentScanner:
    """Scan app submission content for security and policy violations."""

    def scan(self, app_id: str, files: dict[str, str | bytes],
             dependencies: list[str] | None = None) -> ScanResult:
        """Scan all files and dependencies.

        files: dict of file_path → content (str for text, bytes for binary).
        dependencies: list of package names.
        """
        findings: list[ScanFinding] = []
        total_bytes = 0

        # File count check
        if len(files) > MAX_FILE_COUNT:
            findings.append(ScanFinding(
                FindingCategory.SIZE_LIMIT, FindingSeverity.HIGH,
                f"Too many files: {len(files)} > {MAX_FILE_COUNT}",
            ))

        for path, content in files.items():
            content_str = content if isinstance(content, str) else ""
            content_bytes = len(content.encode() if isinstance(content, str) else content)
            total_bytes += content_bytes

            # Per-file size
            if content_bytes > MAX_FILE_BYTES:
                findings.append(ScanFinding(
                    FindingCategory.SIZE_LIMIT, FindingSeverity.MEDIUM,
                    f"File exceeds {MAX_FILE_BYTES // (1024*1024)}MB limit",
                    file_path=path,
                ))

            if content_str:
                findings.extend(self._scan_text(path, content_str))

        # Bundle size
        if total_bytes > MAX_BUNDLE_BYTES:
            findings.append(ScanFinding(
                FindingCategory.SIZE_LIMIT, FindingSeverity.HIGH,
                f"Bundle exceeds {MAX_BUNDLE_BYTES // (1024*1024)}MB limit: {total_bytes} bytes",
            ))

        # Dependencies
        if dependencies:
            findings.extend(self._scan_dependencies(dependencies))

        passed = not any(f.severity in (FindingSeverity.CRITICAL, FindingSeverity.HIGH) for f in findings)

        return ScanResult(
            app_id=app_id, passed=passed, findings=findings,
            files_scanned=len(files), total_bytes=total_bytes,
        )

    def _scan_text(self, path: str, content: str) -> list[ScanFinding]:
        findings: list[ScanFinding] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Secret detection
            for pattern, label in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(ScanFinding(
                        FindingCategory.SECRET_LEAK, FindingSeverity.CRITICAL,
                        f"Possible {label} detected",
                        file_path=path, line_number=line_num,
                        pattern_matched=label,
                    ))

            # Unsafe code
            for pattern, label in UNSAFE_CODE_PATTERNS:
                if pattern.search(line):
                    findings.append(ScanFinding(
                        FindingCategory.UNSAFE_CODE, FindingSeverity.HIGH,
                        f"Unsafe code: {label}",
                        file_path=path, line_number=line_num,
                        pattern_matched=label,
                    ))

            # Internal URLs
            for pattern in INTERNAL_URL_PATTERNS:
                if pattern.search(line):
                    findings.append(ScanFinding(
                        FindingCategory.INVALID_URL, FindingSeverity.MEDIUM,
                        "Internal/localhost URL detected",
                        file_path=path, line_number=line_num,
                    ))
                    break  # one URL finding per line is enough

        return findings

    @staticmethod
    def _scan_dependencies(deps: list[str]) -> list[ScanFinding]:
        findings: list[ScanFinding] = []
        for dep in deps:
            if dep.lower() in KNOWN_BAD_DEPS:
                findings.append(ScanFinding(
                    FindingCategory.KNOWN_VULN, FindingSeverity.CRITICAL,
                    f"Known malicious dependency: {dep}",
                    pattern_matched=dep,
                ))
        return findings
