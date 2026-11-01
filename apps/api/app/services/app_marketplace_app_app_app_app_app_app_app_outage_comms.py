"""Outage communication engine — manage incident communications."""
from __future__ import annotations
import html
import time


def create_update(incident_id: str, status: str, message: str,
                   affected_services: list[str]) -> dict:
    valid_statuses = {"investigating", "identified", "monitoring", "resolved"}
    if status not in valid_statuses:
        return {"created": False, "error": f"invalid status, use {sorted(valid_statuses)}"}
    return {"created": True, "incident_id": incident_id, "status": status,
            "message": html.escape(message), "affected": affected_services,
            "posted_at": time.time()}


def build_status_page_data(incidents: list[dict]) -> dict:
    active = [i for i in incidents if i.get("status") != "resolved"]
    overall = "operational" if not active else "degraded" if len(active) <= 2 else "major_outage"
    affected = set()
    for i in active:
        affected.update(i.get("affected", []))
    return {"overall_status": overall, "active_incidents": len(active),
            "total_incidents": len(incidents), "affected_services": sorted(affected)}
