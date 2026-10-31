"""Error classification engine — classify errors by type and impact."""
from __future__ import annotations

ERROR_CLASSES = {
    "transient": {"retryable": True, "patterns": ["timeout", "connection reset", "503", "429"]},
    "client": {"retryable": False, "patterns": ["400", "401", "403", "422", "validation"]},
    "server": {"retryable": True, "patterns": ["500", "502", "504", "internal"]},
    "data": {"retryable": False, "patterns": ["not found", "404", "constraint", "duplicate"]},
}


def classify_error(message: str, status_code: int = 0) -> dict:
    msg_lower = message.lower()
    code = str(status_code)
    for cls, info in ERROR_CLASSES.items():
        if any(p in msg_lower or p == code for p in info["patterns"]):
            return {"class": cls, "retryable": info["retryable"],
                    "message": message, "status_code": status_code}
    return {"class": "unknown", "retryable": False, "message": message, "status_code": status_code}


def error_distribution(errors: list[dict]) -> dict:
    by_class: dict[str, int] = {}
    retryable = 0
    for e in errors:
        classified = classify_error(e.get("message", ""), e.get("status_code", 0))
        by_class[classified["class"]] = by_class.get(classified["class"], 0) + 1
        if classified["retryable"]:
            retryable += 1
    return {"total": len(errors), "by_class": by_class, "retryable": retryable,
            "non_retryable": len(errors) - retryable}
