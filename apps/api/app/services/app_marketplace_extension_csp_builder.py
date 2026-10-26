"""CSP Builder — construct Content Security Policies for extension sandboxes.

Generates strict CSP headers with configurable directives, nonce injection,
report-only mode, and violation tracking for sandboxed extension UIs.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
import re
from collections import defaultdict


VALID_DIRECTIVES = {
    "default-src", "script-src", "style-src", "img-src", "font-src",
    "connect-src", "frame-src", "media-src", "object-src", "worker-src",
    "child-src", "form-action", "base-uri", "frame-ancestors",
}

DANGEROUS_SOURCES = {"'unsafe-eval'", "'unsafe-inline'", "data:", "blob:"}

VALID_SOURCE_RE = re.compile(
    r"^('self'|'none'|'strict-dynamic'|'nonce-[A-Za-z0-9+/_=-]+'|"
    r"https://[a-z0-9.*-]+(:\d+)?(/[^\s;,]*)?|"
    r"'unsafe-eval'|'unsafe-inline'|data:|blob:)$",
    re.IGNORECASE,
)


def _validate_source(source: str) -> str:
    s = source.strip()
    if not s or ';' in s or ',' in s or '\n' in s:
        raise ValueError(f"Invalid CSP source: {source!r}")
    if not VALID_SOURCE_RE.match(s):
        raise ValueError(f"CSP source not allowed: {s!r}")
    return s


@dataclass
class CSPPolicy:
    extension_id: str
    directives: dict[str, list[str]] = field(default_factory=dict)
    report_only: bool = False
    report_uri: str = ""
    nonce: str = ""

    def __post_init__(self):
        if not self.directives:
            self.directives = {
                "default-src": ["'self'"],
                "script-src": ["'self'"],
                "style-src": ["'self'"],
                "img-src": ["'self'", "https:"],
                "connect-src": ["'self'"],
                "object-src": ["'none'"],
                "base-uri": ["'self'"],
                "frame-ancestors": ["'none'"],
            }


@dataclass
class CSPViolation:
    extension_id: str
    directive: str
    blocked_uri: str
    source_file: str
    line_number: int
    timestamp: float


class CSPBuilderService:
    """Builds and manages Content Security Policies for extensions."""

    def __init__(self):
        self._policies: dict[str, CSPPolicy] = {}
        self._violations: list[CSPViolation] = []

    def create_policy(self, extension_id: str,
                      report_only: bool = False) -> CSPPolicy:
        policy = CSPPolicy(extension_id=extension_id, report_only=report_only)
        self._policies[extension_id] = policy
        return policy

    def set_directive(self, extension_id: str, directive: str,
                      sources: list[str], allow_dangerous: bool = False) -> CSPPolicy:
        policy = self._policies.get(extension_id)
        if not policy:
            raise ValueError("No policy for extension")
        if directive not in VALID_DIRECTIVES:
            raise ValueError(f"Invalid directive: {directive}")
        validated = [_validate_source(s) for s in sources]
        if not allow_dangerous:
            dangerous = [s for s in validated if s.lower() in {d.lower() for d in DANGEROUS_SOURCES}]
            if dangerous:
                raise ValueError(f"Dangerous sources blocked: {dangerous}")
        policy.directives[directive] = validated
        return policy

    def generate_nonce(self, extension_id: str) -> str:
        policy = self._policies.get(extension_id)
        if not policy:
            raise ValueError("No policy for extension")
        nonce = secrets.token_urlsafe(16)
        policy.nonce = nonce
        if "script-src" in policy.directives:
            # Remove old nonces
            policy.directives["script-src"] = [
                s for s in policy.directives["script-src"]
                if not s.startswith("'nonce-")
            ]
            policy.directives["script-src"].append(f"'nonce-{nonce}'")
        return nonce

    def build_header(self, extension_id: str) -> dict:
        policy = self._policies.get(extension_id)
        if not policy:
            return {"header": "", "value": ""}

        parts = []
        for directive, sources in sorted(policy.directives.items()):
            parts.append(f"{directive} {' '.join(sources)}")
        if policy.report_uri:
            parts.append(f"report-uri {policy.report_uri}")

        header_name = ("Content-Security-Policy-Report-Only"
                       if policy.report_only else "Content-Security-Policy")
        return {"header": header_name, "value": "; ".join(parts)}

    def report_violation(self, extension_id: str, directive: str,
                         blocked_uri: str, source_file: str = "",
                         line_number: int = 0) -> None:
        import time
        v = CSPViolation(
            extension_id=extension_id, directive=directive,
            blocked_uri=blocked_uri, source_file=source_file,
            line_number=line_number, timestamp=time.time(),
        )
        self._violations.append(v)

    def get_violations(self, extension_id: str) -> list[dict]:
        return [
            {"directive": v.directive, "blocked_uri": v.blocked_uri,
             "source_file": v.source_file, "line": v.line_number}
            for v in self._violations if v.extension_id == extension_id
        ]

    def get_violation_summary(self, extension_id: str) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for v in self._violations:
            if v.extension_id == extension_id:
                counts[v.directive] += 1
        return dict(counts)
