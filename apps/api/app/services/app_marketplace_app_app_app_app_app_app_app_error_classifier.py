"""Error classifier — categorize and prioritize errors."""
from __future__ import annotations

CATEGORIES = {
    "auth": ["401", "403", "unauthorized", "forbidden", "token"],
    "validation": ["400", "422", "invalid", "required", "schema"],
    "not_found": ["404", "not found", "missing"],
    "rate_limit": ["429", "rate limit", "throttle", "too many"],
    "server": ["500", "502", "503", "504", "internal", "timeout", "unavailable"],
}

SEVERITY = {"server": "critical", "auth": "high", "rate_limit": "medium",
            "validation": "low", "not_found": "low"}


def classify_error(message: str, status_code: int = 0) -> dict:
    msg_lower = message.lower()
    code_str = str(status_code)
    matched = "unknown"
    for cat, keywords in CATEGORIES.items():
        if any(kw in msg_lower or kw == code_str for kw in keywords):
            matched = cat
            break
    return {"category": matched, "severity": SEVERITY.get(matched, "low"),
            "message": message, "status_code": status_code}


def summarize_errors(errors: list[dict]) -> dict:
    by_cat: dict[str, int] = {}
    by_sev: dict[str, int] = {}
    for e in errors:
        c = classify_error(e.get("message", ""), e.get("status_code", 0))
        by_cat[c["category"]] = by_cat.get(c["category"], 0) + 1
        by_sev[c["severity"]] = by_sev.get(c["severity"], 0) + 1
    return {"total": len(errors), "by_category": by_cat, "by_severity": by_sev,
            "has_critical": by_sev.get("critical", 0) > 0}
