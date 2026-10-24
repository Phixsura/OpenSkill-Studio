"""Endpoint usage trend — track usage trends per endpoint over time."""
from __future__ import annotations


def calculate_trend(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "insufficient_data", "data_points": len(snapshots)}
    first_half = snapshots[:len(snapshots)//2]
    second_half = snapshots[len(snapshots)//2:]
    avg_first = sum(s.get("requests", 0) for s in first_half) / len(first_half)
    avg_second = sum(s.get("requests", 0) for s in second_half) / len(second_half)
    change_pct = round((avg_second - avg_first) / max(avg_first, 0.01) * 100, 1)
    trend = "growing" if change_pct > 10 else ("declining" if change_pct < -10 else "stable")
    return {"trend": trend, "change_pct": change_pct, "data_points": len(snapshots),
            "recent_avg": round(avg_second), "older_avg": round(avg_first)}


def top_growing(endpoints: list[dict], limit: int = 5) -> list[dict]:
    with_trend = [(ep, calculate_trend(ep.get("snapshots", []))) for ep in endpoints]
    growing = [(ep, t) for ep, t in with_trend if t.get("trend") == "growing"]
    growing.sort(key=lambda x: -x[1].get("change_pct", 0))
    return [{"endpoint": ep["endpoint"], "change_pct": t["change_pct"],
             "recent_avg": t["recent_avg"]} for ep, t in growing[:limit]]
