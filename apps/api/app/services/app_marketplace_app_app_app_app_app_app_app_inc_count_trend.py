"""Incident count trend — track incident frequency over time."""
from __future__ import annotations

def incident_count_trend(periods: list[dict]) -> dict:
    if len(periods) < 2:
        return {"trend": "stable"}
    counts = [p.get("incidents", 0) for p in periods]
    recent = sum(counts[-3:]) / min(3, len(counts))
    older = sum(counts[:3]) / min(3, len(counts))
    trend = "worsening" if recent > older + 1 else ("improving" if recent < older - 1 else "stable")
    return {"trend": trend, "recent_avg": round(recent, 1), "older_avg": round(older, 1),
            "total": sum(counts), "periods": len(periods)}
