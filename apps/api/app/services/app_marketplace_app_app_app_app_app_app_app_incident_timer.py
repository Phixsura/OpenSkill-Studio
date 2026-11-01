"""Incident response timer — track response, resolution, and communication times."""
from __future__ import annotations


def track_incident_times(incident: dict) -> dict:
    detected = incident.get("detected_at", 0)
    acknowledged = incident.get("acknowledged_at", 0)
    communicated = incident.get("communicated_at", 0)
    resolved = incident.get("resolved_at", 0)
    time_to_ack = round((acknowledged - detected) / 60, 1) if acknowledged else None
    time_to_comm = round((communicated - detected) / 60, 1) if communicated else None
    time_to_resolve = round((resolved - detected) / 60, 1) if resolved else None
    sla_met = time_to_ack is not None and time_to_ack <= incident.get("ack_sla_minutes", 15)
    return {"time_to_ack_minutes": time_to_ack, "time_to_communicate_minutes": time_to_comm,
            "time_to_resolve_minutes": time_to_resolve, "ack_sla_met": sla_met,
            "severity": incident.get("severity", "P3")}


def response_time_report(incidents: list[dict]) -> dict:
    ack_times = [i["time_to_ack_minutes"] for i in incidents if i.get("time_to_ack_minutes") is not None]
    resolve_times = [i["time_to_resolve_minutes"] for i in incidents if i.get("time_to_resolve_minutes") is not None]
    sla_met = sum(1 for i in incidents if i.get("ack_sla_met"))
    return {"total_incidents": len(incidents),
            "avg_ack_minutes": round(sum(ack_times) / max(len(ack_times), 1), 1) if ack_times else 0,
            "avg_resolve_minutes": round(sum(resolve_times) / max(len(resolve_times), 1), 1) if resolve_times else 0,
            "ack_sla_met": sla_met, "ack_sla_pct": round(sla_met / max(len(incidents), 1) * 100, 1)}
