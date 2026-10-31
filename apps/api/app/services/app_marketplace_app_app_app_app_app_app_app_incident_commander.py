"""Incident commander — manage incident lifecycle, timeline, and postmortem."""
from __future__ import annotations
import time


class IncidentCommander:
    def __init__(self):
        self._incidents: dict[str, dict] = {}
        self._seq = 0

    def declare(self, *, title: str, severity: str, commander: str,
                 affected_services: list[str] | None = None) -> dict:
        self._seq += 1
        iid = f"INC-{self._seq:04d}"
        self._incidents[iid] = {
            "id": iid, "title": title, "severity": severity,
            "commander": commander, "status": "investigating",
            "affected": affected_services or [],
            "timeline": [{"action": "declared", "by": commander, "ts": time.time()}],
            "postmortem": None,
        }
        return {"id": iid, "title": title, "severity": severity, "status": "investigating"}

    def update_status(self, iid: str, *, status: str, note: str = "",
                       by: str = "") -> dict:
        inc = self._incidents.get(iid)
        if not inc:
            return {"error": "Incident not found"}
        inc["status"] = status
        inc["timeline"].append({"action": status, "note": note, "by": by, "ts": time.time()})
        return {"id": iid, "status": status}

    def resolve(self, iid: str, *, resolution: str, by: str = "") -> dict:
        r = self.update_status(iid, status="resolved", note=resolution, by=by)
        return r

    def add_postmortem(self, iid: str, *, summary: str, root_cause: str,
                        action_items: list[str]) -> dict:
        inc = self._incidents.get(iid)
        if not inc:
            return {"error": "Incident not found"}
        inc["postmortem"] = {"summary": summary, "root_cause": root_cause,
                              "action_items": action_items}
        return {"id": iid, "postmortem_added": True}

    def list_incidents(self, *, status: str | None = None) -> list[dict]:
        incs = list(self._incidents.values())
        if status:
            incs = [i for i in incs if i["status"] == status]
        return [{"id": i["id"], "title": i["title"], "severity": i["severity"],
                 "status": i["status"], "events": len(i["timeline"])} for i in incs]
