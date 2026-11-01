"""Platform growth tracker — track platform growth metrics."""
from __future__ import annotations


def track_growth(periods: list[dict]) -> dict:
    if len(periods) < 2:
        return {"trend": "insufficient", "periods": len(periods)}
    metrics = {}
    for key in ("users", "apps", "revenue", "api_calls"):
        values = [p.get(key, 0) for p in periods]
        first = values[0] or 1
        last = values[-1]
        growth = round((last - first) / abs(first) * 100, 1)
        metrics[key] = {"first": first, "last": last, "growth_pct": growth,
                         "trend": "up" if growth > 0 else "down" if growth < 0 else "flat"}
    overall_trend = "growing" if all(m["growth_pct"] > 0 for m in metrics.values()) else "mixed"
    return {"metrics": metrics, "periods": len(periods), "overall": overall_trend}


def growth_forecast(current: float, monthly_growth_pct: float, months: int = 6) -> dict:
    projections = []
    val = current
    for m in range(1, months + 1):
        val = round(val * (1 + monthly_growth_pct / 100), 1)
        projections.append({"month": m, "projected": val})
    return {"current": current, "growth_rate": monthly_growth_pct,
            "projections": projections, "final": projections[-1]["projected"]}
