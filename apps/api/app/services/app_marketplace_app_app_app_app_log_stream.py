"""App log stream — real-time log streaming for deployed apps."""

import html
from datetime import datetime, timezone

LOG_LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fatal": 4}
LEVEL_ICONS = {"debug": "🔍", "info": "ℹ️", "warn": "⚠️", "error": "❌", "fatal": "💀"}
LEVEL_COLORS = {"debug": "gray", "info": "blue", "warn": "yellow", "error": "red", "fatal": "red"}


def build_log_stream(*, logs: list[dict], min_level: str = "info",
                        search: str = "") -> dict:
    threshold = LOG_LEVELS.get(min_level, 1)
    filtered = []
    for log in logs:
        level = log.get("level", "info")
        if LOG_LEVELS.get(level, 0) < threshold:
            continue
        msg = log.get("message", "")
        if search and search.lower() not in msg.lower():
            continue
        filtered.append({
            "timestamp": log.get("timestamp", ""),
            "level": level,
            "icon": LEVEL_ICONS.get(level, "📝"),
            "color": LEVEL_COLORS.get(level, "gray"),
            "message": html.escape(msg),
            "source": html.escape(log.get("source", "")),
        })
    error_count = sum(1 for l in filtered if l["level"] in ("error", "fatal"))
    return {"logs": filtered, "total": len(filtered), "error_count": error_count,
            "min_level": min_level, "has_errors": error_count > 0}
