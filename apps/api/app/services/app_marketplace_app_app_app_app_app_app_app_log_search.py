"""Log search engine — search and filter structured logs."""
from __future__ import annotations
import re


def search_logs(logs: list[dict], query: str = "", level: str | None = None,
                service: str | None = None, limit: int = 50) -> dict:
    pattern = re.compile(re.escape(query), re.IGNORECASE) if query else None
    results = []
    for log in logs:
        if level and log.get("level", "").lower() != level.lower():
            continue
        if service and log.get("service", "") != service:
            continue
        if pattern:
            msg = log.get("message", "")
            if not pattern.search(msg):
                continue
        results.append(log)
        if len(results) >= limit:
            break
    levels = {}
    for log in logs:
        lv = log.get("level", "unknown")
        levels[lv] = levels.get(lv, 0) + 1
    return {"results": results, "matched": len(results), "total": len(logs),
            "level_counts": levels, "truncated": len(results) >= limit}


def extract_services(logs: list[dict]) -> list[str]:
    return sorted({log.get("service", "unknown") for log in logs})
