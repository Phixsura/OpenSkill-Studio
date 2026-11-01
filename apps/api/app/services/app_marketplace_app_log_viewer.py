"""Log viewer — structured log search and filtering."""

import re
from datetime import datetime


LOG_LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}


def parse_log_line(*, line: str) -> dict:
    pattern = r"^\[(\d{4}-\d{2}-\d{2}T[\d:]+)\]\s*\[(\w+)\]\s*(.+)$"
    m = re.match(pattern, line)
    if not m:
        return {"parsed": False, "raw": line}
    return {
        "parsed": True,
        "timestamp": m.group(1),
        "level": m.group(2).lower(),
        "message": m.group(3),
    }


def filter_logs(*, logs: list[dict], min_level: str = "debug",
                  search: str | None = None, limit: int = 100) -> dict:
    min_val = LOG_LEVELS.get(min_level, 0)
    filtered = []
    for log in logs:
        level_val = LOG_LEVELS.get(log.get("level", "info"), 20)
        if level_val < min_val:
            continue
        if search and search.lower() not in log.get("message", "").lower():
            continue
        filtered.append(log)
    by_level: dict[str, int] = {}
    for log in filtered:
        lvl = log.get("level", "unknown")
        by_level[lvl] = by_level.get(lvl, 0) + 1
    return {
        "logs": filtered[:limit],
        "total_matched": len(filtered),
        "has_more": len(filtered) > limit,
        "by_level": by_level,
    }
