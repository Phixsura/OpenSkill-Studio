"""Fleet AI Reporting v5 — track automated platform reporting."""
from __future__ import annotations
def fleet_ai_reporting_v5(reporters: list[dict]) -> dict:
    active = [r for r in reporters if r.get("active", True)]
    reports_24h = sum(r.get("reports_24h", 0) for r in reporters)
    recipients = sum(r.get("recipients", 0) for r in reporters)
    templates = sum(r.get("templates", 0) for r in reporters)
    return {"reporters": len(reporters), "active": len(active), "reports_24h": reports_24h,
            "recipients": recipients, "templates": templates, "automated": reports_24h > 0}
