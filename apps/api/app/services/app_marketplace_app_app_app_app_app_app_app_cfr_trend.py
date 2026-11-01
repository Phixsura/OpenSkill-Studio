"""Change failure rate trend — track CFR over time (DORA metric)."""
from __future__ import annotations
def cfr_trend(periods: list[dict]) -> dict:
    if len(periods) < 2: return {"trend": "stable"}
    rates = [p.get("cfr_pct", 0) for p in periods]
    recent = sum(rates[-2:]) / 2
    older = sum(rates[:2]) / 2
    trend = "improving" if recent < older - 2 else ("worsening" if recent > older + 2 else "stable")
    return {"trend": trend, "recent_avg": round(recent, 1), "older_avg": round(older, 1)}
