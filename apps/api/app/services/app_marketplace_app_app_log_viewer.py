"""Log viewer — structured log parsing and filtering."""

import html
import re
from datetime import datetime

LOG_LEVELS = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "FATAL": 4}
LEVEL_ICONS = {"DEBUG": "🔍", "INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌", "FATAL": "💀"}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def parse_log_lines(*, lines: list[str], min_level: str = "DEBUG") -> dict:
    threshold = LOG_LEVELS.get(min_level.upper(), 0)
    entries = []
    for line in lines:
        level = "INFO"
        for lv in LOG_LEVELS:
            if lv in line.upper():
                level = lv
                break
        if LOG_LEVELS.get(level, 0) < threshold:
            continue
        ts_match = TS_RE.match(line)
        entries.append({
            "raw": html.escape(line),
            "level": level,
            "icon": LEVEL_ICONS.get(level, "📝"),
            "timestamp": ts_match.group(0) if ts_match else None,
        })
    error_count = sum(1 for e in entries if e["level"] in ("ERROR", "FATAL"))
    return {"entries": entries, "total": len(entries), "error_count": error_count,
            "has_errors": error_count > 0}
