"""Incident commander — manage incident response workflow."""
from __future__ import annotations

class IncidentCommander:
    def __init__(self):
        self._incidents: dict[str, dict] = {}

    def declare(self, incident_id: str, severity: str, commander: str, title: str) -> dict:
        self._incidents[incident_id] = {"id": incident_id, "severity": severity,
            "commander": commander, "title": title, "status": "active", "actions": []}
        return self._incidents[incident_id]

    def add_action(self, incident_id: str, action: str, assignee: str) -> dict:
        self._incidents[incident_id]["actions"].append({"action": action, "assignee": assignee, "done": False})
        return {"added": True}

    def resolve(self, incident_id: str) -> dict:
        self._incidents[incident_id]["status"] = "resolved"
        return {"id": incident_id, "status": "resolved"}

    def active(self) -> list[dict]:
        return [i for i in self._incidents.values() if i["status"] == "active"]
