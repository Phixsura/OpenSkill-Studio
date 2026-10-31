"""Incident timeline — detailed chronological view of incidents with root cause tracking."""

from datetime import datetime, timezone


def build_incident_timeline(*, incident: dict, updates: list[dict]) -> dict:
    timeline = [{"time": incident.get("created_at"), "type": "opened",
                  "message": f"Incident opened: {incident.get('title', '')}",
                  "severity": incident.get("severity", "medium")}]
    for u in sorted(updates, key=lambda x: x.get("timestamp", "")):
        timeline.append({"time": u["timestamp"], "type": u.get("type", "update"),
                          "message": u.get("message", ""), "author": u.get("author")})
    if incident.get("resolved_at"):
        timeline.append({"time": incident["resolved_at"], "type": "resolved",
                          "message": "Incident resolved"})
    return {"incident_id": incident.get("id"), "timeline": timeline,
            "duration_minutes": _compute_duration(incident), "event_count": len(timeline)}


def _compute_duration(incident: dict) -> int | None:
    start = incident.get("created_at", "")
    end = incident.get("resolved_at")
    if not end:
        return None
    try:
        s = datetime.fromisoformat(start.replace("Z", "+00:00"))
        e = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return int((e - s).total_seconds() / 60)
    except (ValueError, TypeError):
        return None


def compute_mttr(*, incidents: list[dict]) -> dict:
    durations = [_compute_duration(i) for i in incidents if _compute_duration(i) is not None]
    if not durations:
        return {"mttr_minutes": 0, "incident_count": 0}
    return {"mttr_minutes": round(sum(durations) / len(durations), 1),
            "incident_count": len(durations), "min_minutes": min(durations), "max_minutes": max(durations)}
