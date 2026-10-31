"""Log aggregation pipeline — aggregate and summarize log streams."""
from __future__ import annotations
from collections import defaultdict


def aggregate_logs(logs: list[dict]) -> dict:
    by_level: dict[str, int] = defaultdict(int)
    by_source: dict[str, int] = defaultdict(int)
    for log in logs:
        by_level[log.get("level", "info")] += 1
        by_source[log.get("source", "unknown")] += 1
    top_sources = sorted(by_source.items(), key=lambda x: -x[1])[:5]
    return {"total": len(logs), "by_level": dict(by_level),
            "top_sources": [{"source": s, "count": c} for s, c in top_sources],
            "error_count": by_level.get("error", 0) + by_level.get("fatal", 0),
            "has_errors": by_level.get("error", 0) + by_level.get("fatal", 0) > 0}


def extract_patterns(logs: list[dict], min_count: int = 2) -> list[dict]:
    msg_counts: dict[str, int] = defaultdict(int)
    for log in logs:
        msg = log.get("message", "")
        key = msg.split(":")[0].strip() if ":" in msg else msg[:50]
        msg_counts[key] += 1
    patterns = [{"pattern": k, "count": v} for k, v in msg_counts.items() if v >= min_count]
    return sorted(patterns, key=lambda x: -x["count"])
