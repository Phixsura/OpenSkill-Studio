"""Error classifier — automatically categorize and prioritize app errors."""

from collections import defaultdict


ERROR_PATTERNS = {
    "connection": ["ECONNREFUSED", "ECONNRESET", "ETIMEDOUT", "connection refused"],
    "auth": ["401", "403", "unauthorized", "forbidden", "token expired"],
    "validation": ["422", "validation error", "invalid", "required field"],
    "rate_limit": ["429", "rate limit", "too many requests"],
    "server": ["500", "internal server error", "unhandled exception"],
    "timeout": ["timeout", "deadline exceeded", "504"],
}


def classify_error(*, message: str) -> dict:
    msg_lower = message.lower()
    for category, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in msg_lower:
                return {"category": category, "pattern": pattern, "severity": _get_severity(category)}
    return {"category": "unknown", "pattern": None, "severity": "medium"}


def _get_severity(category: str) -> str:
    severities = {"connection": "high", "auth": "medium", "validation": "low",
                   "rate_limit": "medium", "server": "critical", "timeout": "high"}
    return severities.get(category, "medium")


def aggregate_errors_by_category(*, errors: list[dict]) -> dict:
    by_cat = defaultdict(int)
    for e in errors:
        classified = classify_error(message=e.get("message", ""))
        by_cat[classified["category"]] += 1
    top = sorted(by_cat.items(), key=lambda x: -x[1])
    return {"categories": dict(top), "total": len(errors),
            "top_category": top[0][0] if top else None}
