"""Content Security Policy Engine — build and enforce CSP for extension sandboxes.

Implements:
- Directive-level policy building with source validation
- Nonce generation for inline scripts/styles
- Policy inheritance (base + extension-specific overrides)
- Violation report collection and pattern analysis
- Strict mode with no unsafe-inline/unsafe-eval
"""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import re
from collections import Counter

VALID_DIRECTIVES = {
    "default-src", "script-src", "style-src", "img-src", "font-src",
    "connect-src", "frame-src", "object-src", "base-uri", "form-action",
    "frame-ancestors", "worker-src", "manifest-src",
}

SOURCE_RE = re.compile(
    r"^('self'|'none'|'unsafe-inline'|'unsafe-eval'|'strict-dynamic'|"
    r"'nonce-[A-Za-z0-9+/=]+'|"
    r"https?://[a-zA-Z0-9.*-]+(?::\d+)?(?:/[^\s]*)?"
    r"|data:|blob:|wss?://[a-zA-Z0-9.*-]+)$"
)

BLOCKED_SOURCES = {"'unsafe-inline'", "'unsafe-eval'"}


@dataclass
class CspViolation:
    extension_id: str
    directive: str
    blocked_uri: str
    source_file: str = ""
    timestamp: float = 0.0


@dataclass
class CspPolicy:
    extension_id: str
    directives: dict[str, list[str]] = field(default_factory=dict)
    strict: bool = True
    nonces: list[str] = field(default_factory=list)


class CspEngineService:
    BASE_POLICY = {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'"],
        "img-src": ["'self'", "data:", "https://*.openskill.dev"],
        "connect-src": ["'self'", "https://api.openskill.dev"],
        "frame-ancestors": ["'none'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
    }

    def __init__(self):
        self._policies: dict[str, CspPolicy] = {}
        self._violations: list[CspViolation] = []

    def create_policy(self, extension_id: str, strict: bool = True) -> CspPolicy:
        policy = CspPolicy(extension_id=extension_id, strict=strict,
                           directives={k: list(v) for k, v in self.BASE_POLICY.items()})
        self._policies[extension_id] = policy
        return policy

    def add_source(self, extension_id: str, directive: str,
                   source: str) -> tuple[bool, str]:
        policy = self._policies.get(extension_id)
        if not policy:
            return False, "Policy not found"
        if directive not in VALID_DIRECTIVES:
            return False, f"Invalid directive: {directive}"
        if not SOURCE_RE.match(source):
            return False, f"Invalid source format: {source}"
        if policy.strict and source in BLOCKED_SOURCES:
            return False, f"Source {source} blocked in strict mode"
        if directive not in policy.directives:
            policy.directives[directive] = []
        if source not in policy.directives[directive]:
            policy.directives[directive].append(source)
        return True, "Added"

    def generate_nonce(self, extension_id: str) -> str | None:
        policy = self._policies.get(extension_id)
        if not policy:
            return None
        nonce = secrets.token_urlsafe(16)
        policy.nonces.append(nonce)
        # Add nonce to script-src
        nonce_src = f"'nonce-{nonce}'"
        if "script-src" not in policy.directives:
            policy.directives["script-src"] = ["'self'"]
        policy.directives["script-src"].append(nonce_src)
        return nonce

    def render(self, extension_id: str) -> str:
        policy = self._policies.get(extension_id)
        if not policy:
            return ""
        parts = []
        for directive, sources in sorted(policy.directives.items()):
            parts.append(f"{directive} {' '.join(sources)}")
        return "; ".join(parts)

    def report_violation(self, extension_id: str, directive: str,
                         blocked_uri: str, source_file: str = "") -> None:
        import time
        self._violations.append(CspViolation(
            extension_id=extension_id, directive=directive,
            blocked_uri=blocked_uri, source_file=source_file,
            timestamp=time.time()))

    def get_violation_summary(self, extension_id: str) -> dict:
        ext_violations = [v for v in self._violations if v.extension_id == extension_id]
        by_directive = Counter(v.directive for v in ext_violations)
        by_uri = Counter(v.blocked_uri for v in ext_violations)
        return {
            "total": len(ext_violations),
            "by_directive": dict(by_directive.most_common(10)),
            "top_blocked": dict(by_uri.most_common(5)),
        }
