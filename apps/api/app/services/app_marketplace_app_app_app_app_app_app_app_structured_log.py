"""Structured log parser — parse JSON logs and compute aggregates."""
from __future__ import annotations
import json


def parse_logs(lines: list[str]) -> dict:
    parsed = []
    errors = 0
    for line in lines:
        try:
            entry = json.loads(line)
            parsed.append(entry)
        except (json.JSONDecodeError, TypeError):
            errors += 1
    by_level: dict[str, int] = {}
    by_service: dict[str, int] = {}
    for e in parsed:
        lv = e.get("level", "unknown").lower()
        svc = e.get("service", "unknown")
        by_level[lv] = by_level.get(lv, 0) + 1
        by_service[svc] = by_service.get(svc, 0) + 1
    return {
        "total": len(lines), "parsed": len(parsed), "parse_errors": errors,
        "by_level": by_level, "by_service": by_service,
        "error_count": by_level.get("error", 0) + by_level.get("fatal", 0),
        "has_errors": by_level.get("error", 0) + by_level.get("fatal", 0) > 0,
    }


def filter_logs(parsed: list[dict], *, level: str | None = None,
                 service: str | None = None, search: str | None = None) -> list[dict]:
    result = parsed
    if level:
        result = [e for e in result if e.get("level", "").lower() == level.lower()]
    if service:
        result = [e for e in result if e.get("service") == service]
    if search:
        result = [e for e in result if search.lower() in json.dumps(e).lower()]
    return result
