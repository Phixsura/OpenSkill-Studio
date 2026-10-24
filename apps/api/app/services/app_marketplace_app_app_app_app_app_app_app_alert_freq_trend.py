"""Alert frequency trend — track how alert volume changes over time."""
from __future__ import annotations
def alert_freq_trend(periods: list[dict]) -> dict:
    if len(periods) < 2: return {"trend": "stable"}
    counts = [p.get("alerts", 0) for p in periods]
    recent = sum(counts[-2:]) / 2
    older = sum(counts[:2]) / 2
    trend = "noisier" if recent > older + 5 else ("quieter" if recent < older - 5 else "stable")
    return {"trend": trend, "recent_avg": round(recent, 1), "older_avg": round(older, 1), "total": sum(counts)}
