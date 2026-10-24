"""Fleet SLA report — monthly SLA compliance report."""
from __future__ import annotations
def fleet_sla_report(month: dict) -> dict:
    uptime = month.get("uptime_pct", 99.9)
    target = month.get("target_pct", 99.9)
    met = uptime >= target
    credits = round(max(0, (target - uptime)) * 1000, 2) if not met else 0
    return {"uptime_pct": uptime, "target_pct": target, "met": met,
            "credits_usd": credits, "month": month.get("month", "unknown")}
