"""Log search engine — full-text search over structured log entries."""
from __future__ import annotations
import re


def search_logs(logs: list[dict], *, query: str, level: str | None = None,
                service: str | None = None, limit: int = 50) -> dict:
    pattern = re.compile(re.escape(query), re.IGNORECASE) if query else None
    results = []
    for log in logs:
        if level and log.get("level", "").lower() != level.lower():
            continue
        if service and log.get("service", "") != service:
            continue
        msg = log.get("message", "")
        if pattern and not pattern.search(msg):
            continue
        results.append(log)
        if len(results) >= limit:
            break
    by_level: dict[str, int] = {}
    for r in results:
        lv = r.get("level", "info")
        by_level[lv] = by_level.get(lv, 0) + 1
    return {"total": len(results), "query": query, "results": results,
            "by_level": by_level, "truncated": len(results) >= limit}


def parse_log_line(line: str) -> dict:
    m = re.match(r"\[(\w+)]\s+(\S+)\s+(.*)", line)
    if m:
        return {"level": m.group(1).lower(), "service": m.group(2), "message": m.group(3)}
    return {"level": "info", "service": "unknown", "message": line}
