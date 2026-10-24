"""Priority queue analyzer — analyze queue depth and wait times by priority."""
from __future__ import annotations
from collections import defaultdict


def analyze_queue(items: list[dict]) -> dict:
    by_priority: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_wait_ms": 0})
    for item in items:
        p = item.get("priority", "normal")
        by_priority[p]["count"] += 1
        by_priority[p]["total_wait_ms"] += item.get("wait_ms", 0)
    priorities = []
    for p in ["critical", "high", "normal", "low", "background"]:
        if p in by_priority:
            data = by_priority[p]
            avg_wait = round(data["total_wait_ms"] / max(data["count"], 1), 1)
            priorities.append({"priority": p, "count": data["count"], "avg_wait_ms": avg_wait})
    total = sum(d["count"] for d in by_priority.values())
    return {"priorities": priorities, "total_queued": total,
            "deepest": max(priorities, key=lambda p: p["count"])["priority"] if priorities else "none"}


def queue_health(depth: int, max_depth: int = 1000) -> dict:
    pct = round(depth / max(max_depth, 1) * 100, 1)
    status = "healthy" if pct < 50 else ("warning" if pct < 80 else "critical")
    return {"depth": depth, "max_depth": max_depth, "pct": pct, "status": status}
