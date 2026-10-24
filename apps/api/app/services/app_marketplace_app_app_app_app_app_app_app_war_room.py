"""Incident war room — coordinate real-time incident response."""
from __future__ import annotations
import time


def create_war_room(incident_id: str, title: str, severity: str,
                      commander: str) -> dict:
    return {"incident_id": incident_id, "title": title, "severity": severity,
            "commander": commander, "status": "active",
            "participants": [commander], "updates": [],
            "created_at": time.time()}


def add_update(room: dict, author: str, message: str) -> dict:
    update = {"author": author, "message": message, "timestamp": time.time(),
              "seq": len(room["updates"]) + 1}
    room["updates"].append(update)
    if author not in room["participants"]:
        room["participants"].append(author)
    return {"added": True, "seq": update["seq"],
            "participants": len(room["participants"])}


def close_war_room(room: dict, resolution: str) -> dict:
    room["status"] = "resolved"
    duration_min = round((time.time() - room["created_at"]) / 60, 1)
    return {"closed": True, "resolution": resolution,
            "duration_min": duration_min, "updates": len(room["updates"]),
            "participants": len(room["participants"])}
