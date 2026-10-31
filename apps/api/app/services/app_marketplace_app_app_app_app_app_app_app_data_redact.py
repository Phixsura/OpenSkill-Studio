"""Data redaction engine — redact PII and sensitive data from payloads."""
from __future__ import annotations
import re
import html


_EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+')
_PHONE_RE = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
_SSN_RE = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')


def redact_text(text: str, patterns: list[str] | None = None) -> dict:
    redacted = text
    count = 0
    for pattern, replacement in [
        (_EMAIL_RE, "[EMAIL]"), (_PHONE_RE, "[PHONE]"), (_SSN_RE, "[SSN]"),
    ]:
        matches = pattern.findall(redacted)
        count += len(matches)
        redacted = pattern.sub(replacement, redacted)
    return {"original_length": len(text), "redacted_length": len(redacted),
            "redactions": count, "text": redacted}


def redact_dict(data: dict, sensitive_keys: list[str]) -> dict:
    result = {}
    redacted_count = 0
    for k, v in data.items():
        if k in sensitive_keys:
            result[k] = "***REDACTED***"
            redacted_count += 1
        elif isinstance(v, str):
            r = redact_text(v)
            result[k] = r["text"]
            redacted_count += r["redactions"]
        else:
            result[k] = v
    return {"data": result, "redacted_fields": redacted_count}
