"""Fleet AI Usage Reporter — track AI consumption reporting and insights."""
from __future__ import annotations
def fleet_ai_usage_reporter(reporters: list[dict]) -> dict:
    active = [r for r in reporters if r.get("active", True)]
    reports_24h = sum(r.get("reports_24h", 0) for r in reporters)
    recipients = sum(r.get("recipients", 0) for r in reporters)
    insights_generated = sum(r.get("insights", 0) for r in reporters)
    return {"reporters": len(reporters), "active": len(active), "reports_24h": reports_24h,
            "recipients": recipients, "insights": insights_generated, "informing": reports_24h > 0}
