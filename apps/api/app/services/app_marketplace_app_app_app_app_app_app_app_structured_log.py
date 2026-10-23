"""Structured logging formatter — format logs as structured JSON."""
from __future__ import annotations
import time
import html


def format_log(level: str, message: str, context: dict | None = None,
               service: str = "", trace_id: str = "") -> dict:
    return {"timestamp": time.time(), "level": level.upper(),
            "message": html.escape(message), "service": service,
            "trace_id": trace_id, "context": context or {},
            "formatted": f"[{level.upper()}] {html.escape(message)}"}


def parse_log_line(line: str) -> dict:
    parts = line.strip().split(" ", 2)
    if len(parts) >= 3 and parts[0].startswith("["):
        level = parts[0].strip("[]")
        return {"level": level, "message": parts[2] if len(parts) > 2 else parts[1],
                "parsed": True}
    return {"level": "unknown", "message": line.strip(), "parsed": False}


def aggregate_log_levels(logs: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for log in logs:
        lv = log.get("level", "UNKNOWN")
        counts[lv] = counts.get(lv, 0) + 1
    total = sum(counts.values())
    return {"total": total, "by_level": counts,
            "error_pct": round(counts.get("ERROR", 0) / max(total, 1) * 100, 1)}
