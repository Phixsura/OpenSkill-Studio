"""Error Classifier — categorize errors by type, severity, and root cause.

Implements:
- Error type classification (transient, permanent, configuration, resource)
- Severity scoring (info, warning, error, critical, fatal)
- Retryability determination
- Root cause pattern matching
- Error grouping by fingerprint
- Suggested remediation per error class
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
from collections import defaultdict


@dataclass
class ClassifiedError:
    original: str
    error_type: str   # transient, permanent, configuration, resource, authentication, validation
    severity: str     # info, warning, error, critical, fatal
    retryable: bool
    category: str     # network, database, auth, input, system, unknown
    fingerprint: str
    remediation: str = ""


PATTERNS = [
    # (regex, error_type, severity, retryable, category, remediation)
    (r"timeout|timed?\s*out|deadline exceeded", "transient", "warning", True, "network",
     "Retry with exponential backoff. Check network latency."),
    (r"connection\s*(refused|reset|closed|lost)", "transient", "error", True, "network",
     "Check if the target service is running. Retry after delay."),
    (r"dns|resolve|lookup", "transient", "error", True, "network",
     "DNS resolution failed. Check DNS configuration."),
    (r"rate\s*limit|throttl|429|too many requests", "transient", "warning", True, "network",
     "Back off and retry with exponential delay. Consider rate limit increase."),
    (r"out\s*of\s*memory|oom|memory\s*exceeded|heap", "resource", "critical", False, "system",
     "Increase memory allocation or optimize memory usage."),
    (r"disk\s*(full|space)|no\s*space|ENOSPC", "resource", "critical", False, "system",
     "Free disk space or increase storage allocation."),
    (r"(cpu|load)\s*(high|exceeded|100%)", "resource", "warning", True, "system",
     "Scale horizontally or optimize CPU-intensive operations."),
    (r"unauthorized|401|forbidden|403|auth.*fail", "permanent", "error", False, "auth",
     "Check credentials, API keys, or token expiry."),
    (r"not\s*found|404|does\s*not\s*exist|missing", "permanent", "warning", False, "input",
     "Verify the resource exists and the identifier is correct."),
    (r"invalid|malformed|bad\s*request|400|422|validation", "validation", "warning", False, "input",
     "Fix the request payload according to the API specification."),
    (r"duplicate|already\s*exists|conflict|409", "permanent", "warning", False, "input",
     "Resource already exists. Use update instead of create."),
    (r"deadlock|lock\s*timeout|serialization", "transient", "error", True, "database",
     "Retry the transaction. Consider reducing lock scope."),
    (r"(database|db|sql|postgres|mysql).*error", "transient", "error", True, "database",
     "Check database connectivity and query syntax."),
    (r"internal\s*server|500|unexpected|panic|crash", "transient", "critical", True, "system",
     "Internal error. Check server logs for stack trace."),
    (r"ssl|tls|certificate|handshake", "configuration", "error", False, "network",
     "Check SSL/TLS certificates and configuration."),
]


class ErrorClassifierService:
    def __init__(self):
        self._compiled = [(re.compile(p, re.IGNORECASE), et, sev, retry, cat, rem)
                          for p, et, sev, retry, cat, rem in PATTERNS]
        self._counts: dict[str, int] = defaultdict(int)

    def classify(self, error_message: str) -> ClassifiedError:
        """Classify an error message."""
        for pattern, error_type, severity, retryable, category, remediation in self._compiled:
            if pattern.search(error_message):
                fp = f"{category}:{error_type}:{pattern.pattern[:30]}"
                self._counts[fp] += 1
                return ClassifiedError(
                    original=error_message, error_type=error_type,
                    severity=severity, retryable=retryable,
                    category=category, fingerprint=fp,
                    remediation=remediation)

        # Unknown error
        fp = f"unknown:{error_message[:50]}"
        self._counts[fp] += 1
        return ClassifiedError(
            original=error_message, error_type="unknown",
            severity="error", retryable=False, category="unknown",
            fingerprint=fp, remediation="Investigate the error in application logs.")

    def classify_batch(self, errors: list[str]) -> dict:
        """Classify multiple errors and return summary."""
        classified = [self.classify(e) for e in errors]
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        by_category = defaultdict(int)
        retryable_count = 0
        for c in classified:
            by_type[c.error_type] += 1
            by_severity[c.severity] += 1
            by_category[c.category] += 1
            if c.retryable:
                retryable_count += 1
        return {
            "total": len(classified),
            "by_type": dict(by_type),
            "by_severity": dict(by_severity),
            "by_category": dict(by_category),
            "retryable_pct": round(retryable_count / max(1, len(classified)) * 100, 1),
        }

    def get_top_errors(self, limit: int = 10) -> list[tuple[str, int]]:
        return sorted(self._counts.items(), key=lambda x: x[1], reverse=True)[:limit]
