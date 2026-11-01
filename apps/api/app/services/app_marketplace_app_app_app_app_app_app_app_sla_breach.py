"""SLA breach detector — detect and report SLA breaches in real-time."""
from __future__ import annotations


def detect_breaches(services: list[dict]) -> dict:
    breaches = []
    for svc in services:
        target = svc.get("sla_target", 99.9)
        actual = svc.get("uptime_pct", 100)
        if actual < target:
            gap = round(target - actual, 3)
            severity = "critical" if gap > 1 else ("high" if gap > 0.5 else "warning")
            breaches.append({"service": svc["name"], "target": target,
                             "actual": actual, "gap": gap, "severity": severity})
    breaches.sort(key=lambda b: -b["gap"])
    return {"breaches": breaches, "total_services": len(services),
            "breached": len(breaches), "all_met": len(breaches) == 0}


def breach_impact(breach: dict, monthly_revenue: float) -> dict:
    sla_credit_pct = min(30, breach["gap"] * 10)
    credit = round(monthly_revenue * sla_credit_pct / 100, 2)
    return {"service": breach["service"], "sla_credit_pct": sla_credit_pct,
            "estimated_credit": credit}
