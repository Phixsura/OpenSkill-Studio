"""Outage detector — detect and classify platform outages."""
from __future__ import annotations


def detect_outage(services: list[dict]) -> dict:
    down = [s for s in services if s.get("status") == "down"]
    degraded = [s for s in services if s.get("status") == "degraded"]
    total = len(services)
    if not down and not degraded:
        return {"outage": False, "classification": "none", "affected": 0}
    down_pct = len(down) / max(total, 1) * 100
    if down_pct > 50:
        classification = "major"
    elif down_pct > 0:
        classification = "partial"
    elif degraded:
        classification = "degraded"
    else:
        classification = "none"
    affected_services = [s["name"] for s in down + degraded]
    return {"outage": True, "classification": classification,
            "affected": len(affected_services),
            "affected_services": affected_services,
            "down_count": len(down), "degraded_count": len(degraded)}


def outage_impact(outage: dict, total_users: int) -> dict:
    affected_pct = outage.get("affected", 0) / max(outage.get("affected", 0) + 5, 1) * 100
    estimated_users = round(total_users * affected_pct / 100)
    severity = "critical" if outage.get("classification") == "major" else (
        "high" if outage.get("classification") == "partial" else "medium")
    return {"severity": severity, "estimated_users_affected": estimated_users,
            "classification": outage.get("classification", "none")}
