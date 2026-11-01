"""SLA credit calculator — calculate SLA credits owed to customers."""
from __future__ import annotations


def calculate_credit(uptime_pct: float, sla_target: float, monthly_revenue: float,
                     credit_tiers: list[dict] | None = None) -> dict:
    if uptime_pct >= sla_target:
        return {"credit_pct": 0, "credit_amount": 0, "sla_met": True, "uptime_pct": uptime_pct}
    tiers = credit_tiers or [
        {"min_uptime": 99.0, "credit_pct": 10},
        {"min_uptime": 95.0, "credit_pct": 25},
        {"min_uptime": 0, "credit_pct": 50},
    ]
    credit_pct = 0
    for tier in tiers:
        if uptime_pct >= tier["min_uptime"]:
            credit_pct = tier["credit_pct"]
            break
    credit_amount = round(monthly_revenue * credit_pct / 100, 2)
    return {"credit_pct": credit_pct, "credit_amount": credit_amount,
            "sla_met": False, "uptime_pct": uptime_pct,
            "gap": round(sla_target - uptime_pct, 3)}
