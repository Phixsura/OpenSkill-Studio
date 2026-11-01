"""Incident responder — coordinate incident response workflows."""
from __future__ import annotations
import time


def create_incident(title: str, severity: str, reporter: str,
                     affected_services: list[str]) -> dict:
    return {"title": title, "severity": severity, "reporter": reporter,
            "affected": affected_services, "status": "investigating",
            "responders": [reporter], "created_at": time.time(),
            "timeline": [{"action": "created", "by": reporter, "at": time.time()}]}


def assign_responder(incident: dict, responder: str) -> dict:
    if responder not in incident["responders"]:
        incident["responders"].append(responder)
    incident["timeline"].append({"action": "responder_added", "by": responder, "at": time.time()})
    return {"assigned": True, "responder_count": len(incident["responders"])}


def update_status(incident: dict, new_status: str, by: str) -> dict:
    valid = {"investigating", "identified", "monitoring", "resolved"}
    if new_status not in valid:
        return {"updated": False, "error": "invalid_status"}
    incident["status"] = new_status
    incident["timeline"].append({"action": f"status_{new_status}", "by": by, "at": time.time()})
    return {"updated": True, "status": new_status, "timeline_length": len(incident["timeline"])}


def incident_metrics(incidents: list[dict]) -> dict:
    by_sev: dict[str, int] = {}
    resolved = 0
    for i in incidents:
        by_sev[i["severity"]] = by_sev.get(i["severity"], 0) + 1
        if i["status"] == "resolved":
            resolved += 1
    return {"total": len(incidents), "resolved": resolved,
            "open": len(incidents) - resolved, "by_severity": by_sev}
