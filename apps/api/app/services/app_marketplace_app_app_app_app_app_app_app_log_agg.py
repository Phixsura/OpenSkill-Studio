"""Log aggregation pipeline — aggregate logs from multiple sources."""
from __future__ import annotations


def aggregate_logs(sources: list[dict]) -> dict:
    total_lines = 0
    by_level: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for src in sources:
        name = src.get("name", "unknown")
        logs = src.get("logs", [])
        by_source[name] = len(logs)
        total_lines += len(logs)
        for log in logs:
            lv = log.get("level", "info")
            by_level[lv] = by_level.get(lv, 0) + 1
    error_count = by_level.get("error", 0) + by_level.get("fatal", 0)
    return {"total_lines": total_lines, "source_count": len(sources),
            "by_level": by_level, "by_source": by_source,
            "error_count": error_count,
            "error_rate": round(error_count / max(total_lines, 1) * 100, 2)}


def find_patterns(logs: list[dict], pattern: str) -> dict:
    matches = [l for l in logs if pattern.lower() in l.get("message", "").lower()]
    return {"pattern": pattern, "matches": len(matches), "total": len(logs),
            "match_rate": round(len(matches) / max(len(logs), 1) * 100, 1)}
