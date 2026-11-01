"""Service latency trend — track latency changes over time periods."""
from __future__ import annotations

def latency_trend(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "stable", "data_points": len(snapshots)}
    first = snapshots[:len(snapshots)//2]
    second = snapshots[len(snapshots)//2:]
    avg_first = sum(s.get("p99_ms", 0) for s in first) / len(first)
    avg_second = sum(s.get("p99_ms", 0) for s in second) / len(second)
    change_pct = round((avg_second - avg_first) / max(avg_first, 0.01) * 100, 1)
    trend = "worsening" if change_pct > 10 else ("improving" if change_pct < -10 else "stable")
    return {"trend": trend, "change_pct": change_pct, "recent_p99": round(avg_second, 1),
            "older_p99": round(avg_first, 1), "data_points": len(snapshots)}
