"""Capacity headroom calculator — calculate remaining capacity headroom."""
from __future__ import annotations


def calculate_headroom(services: list[dict]) -> dict:
    results = []
    for s in services:
        current = s.get("current_rps", 0)
        capacity = s.get("max_rps", 1000)
        headroom_rps = capacity - current
        headroom_pct = round(headroom_rps / max(capacity, 1) * 100, 1)
        status = "critical" if headroom_pct < 10 else ("warning" if headroom_pct < 30 else "ok")
        results.append({"service": s["name"], "current_rps": current,
                        "max_rps": capacity, "headroom_rps": headroom_rps,
                        "headroom_pct": headroom_pct, "status": status})
    min_headroom = min(results, key=lambda r: r["headroom_pct"]) if results else None
    return {"services": sorted(results, key=lambda r: r["headroom_pct"]),
            "bottleneck": min_headroom["service"] if min_headroom else "",
            "min_headroom_pct": min_headroom["headroom_pct"] if min_headroom else 100}
