"""Structured log formatter — format logs as JSON with standard fields."""
from __future__ import annotations
import time


def format_log(level: str, message: str, service: str = "", extra: dict | None = None) -> dict:
    log = {"timestamp": time.time(), "level": level.upper(), "message": message,
           "service": service}
    if extra:
        log["extra"] = extra
    return log


def parse_log_line(line: str) -> dict:
    parts = line.strip().split(" ", 3)
    if len(parts) < 3:
        return {"raw": line, "parsed": False}
    return {"timestamp": parts[0], "level": parts[1].strip("[]"),
            "message": parts[2] if len(parts) == 3 else parts[3], "parsed": True}


def log_stats(logs: list[dict]) -> dict:
    by_level: dict[str, int] = {}
    by_service: dict[str, int] = {}
    for log in logs:
        level = log.get("level", "UNKNOWN")
        by_level[level] = by_level.get(level, 0) + 1
        svc = log.get("service", "unknown")
        by_service[svc] = by_service.get(svc, 0) + 1
    return {"total": len(logs), "by_level": by_level, "by_service": by_service}
