"""Service uptime trend — track uptime changes over reporting periods."""
from __future__ import annotations

def uptime_trend(periods: list[dict]) -> dict:
    if len(periods) < 2:
        return {"trend": "stable"}
    uptimes = [p.get("uptime_pct", 100) for p in periods]
    recent = sum(uptimes[-3:]) / min(3, len(uptimes))
    older = sum(uptimes[:3]) / min(3, len(uptimes))
    trend = "improving" if recent > older + 0.1 else ("declining" if recent < older - 0.1 else "stable")
    return {"trend": trend, "recent": round(recent, 3), "older": round(older, 3),
            "current": uptimes[-1], "periods": len(periods)}
