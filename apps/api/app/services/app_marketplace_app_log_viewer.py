"""Log viewer — structured log search and filtering for app debugging."""

import re


def filter_logs(*, logs: list[dict], level: str | None = None, search: str | None = None,
                  limit: int = 100) -> list[dict]:
    result = logs
    if level:
        result = [l for l in result if l.get("level") == level]
    if search:
        pattern = re.compile(re.escape(search), re.IGNORECASE)
        result = [l for l in result if pattern.search(l.get("message", ""))]
    return result[:limit]


def aggregate_log_levels(*, logs: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for l in logs:
        lvl = l.get("level", "unknown")
        counts[lvl] = counts.get(lvl, 0) + 1
    return {"counts": counts, "total": len(logs),
            "has_errors": counts.get("error", 0) > 0 or counts.get("fatal", 0) > 0}


def format_log_entry(*, entry: dict) -> str:
    ts = entry.get("timestamp", "")[:19]
    level = entry.get("level", "info").upper().ljust(5)
    msg = entry.get("message", "")
    return f"[{ts}] {level} {msg}"
