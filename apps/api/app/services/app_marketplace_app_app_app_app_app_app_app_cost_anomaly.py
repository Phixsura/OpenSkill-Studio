"""Cost anomaly detector — flag unexpected cost spikes across services."""
from __future__ import annotations
import math


def detect_cost_anomalies(daily_costs: list[dict], *, threshold_pct: float = 50) -> dict:
    if len(daily_costs) < 3:
        return {"anomalies": [], "error": "Need at least 3 days of data"}
    amounts = [d.get("amount", 0) for d in daily_costs]
    mean = sum(amounts) / len(amounts)
    std = math.sqrt(sum((a - mean) ** 2 for a in amounts) / len(amounts))
    anomalies = []
    for d in daily_costs:
        amt = d.get("amount", 0)
        if mean > 0:
            deviation_pct = abs(amt - mean) / mean * 100
        else:
            deviation_pct = 0
        if deviation_pct >= threshold_pct and amt > mean:
            anomalies.append({
                "date": d.get("date", ""), "amount": amt,
                "expected": round(mean, 2), "deviation_pct": round(deviation_pct, 1),
                "service": d.get("service", ""),
                "display": f"${amt:,.2f} (+{deviation_pct:.0f}%)",
            })
    total_spend = sum(amounts)
    return {
        "anomalies": anomalies, "count": len(anomalies),
        "mean_daily": round(mean, 2), "std": round(std, 2),
        "total_spend": round(total_spend, 2),
        "total_display": f"${total_spend:,.2f}",
        "has_anomalies": len(anomalies) > 0,
    }
