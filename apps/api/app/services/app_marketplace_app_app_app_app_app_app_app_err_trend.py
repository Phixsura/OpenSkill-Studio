"""Service error trend — track error rate changes over time."""
from __future__ import annotations

def error_trend(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "stable"}
    first = snapshots[:len(snapshots)//2]
    second = snapshots[len(snapshots)//2:]
    avg_first = sum(s.get("error_rate", 0) for s in first) / len(first)
    avg_second = sum(s.get("error_rate", 0) for s in second) / len(second)
    change = round(avg_second - avg_first, 3)
    trend = "worsening" if change > 0.5 else ("improving" if change < -0.5 else "stable")
    return {"trend": trend, "change": change, "recent_rate": round(avg_second, 3),
            "older_rate": round(avg_first, 3)}
