"""Incident timeline builder — create detailed incident timelines."""
from __future__ import annotations
import time


def build_timeline(events: list[dict]) -> dict:
    sorted_events = sorted(events, key=lambda e: e.get("timestamp", 0))
    if len(sorted_events) >= 2:
        duration_min = round((sorted_events[-1]["timestamp"] - sorted_events[0]["timestamp"]) / 60, 1)
    else:
        duration_min = 0
    by_type: dict[str, int] = {}
    for e in sorted_events:
        by_type[e.get("type", "update")] = by_type.get(e.get("type", "update"), 0) + 1
    return {"events": sorted_events, "event_count": len(sorted_events),
            "duration_min": duration_min, "by_type": by_type,
            "started": sorted_events[0]["timestamp"] if sorted_events else 0}


def time_to_resolve(incidents: list[dict]) -> dict:
    times = []
    for i in incidents:
        if i.get("resolved_at") and i.get("created_at"):
            times.append(round((i["resolved_at"] - i["created_at"]) / 60, 1))
    if not times:
        return {"avg_min": 0, "p50_min": 0, "p99_min": 0, "count": 0}
    s = sorted(times)
    return {"avg_min": round(sum(s) / len(s), 1), "p50_min": s[len(s) // 2],
            "p99_min": s[int(len(s) * 0.99)], "count": len(s),
            "fastest_min": s[0], "slowest_min": s[-1]}
