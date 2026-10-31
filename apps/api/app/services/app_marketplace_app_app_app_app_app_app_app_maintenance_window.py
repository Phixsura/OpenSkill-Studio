"""Maintenance window scheduler — schedule and track planned maintenance."""
from __future__ import annotations


class MaintenanceScheduler:
    def __init__(self):
        self._windows: list[dict] = []

    def schedule(self, *, title: str, start: str, end: str,
                  affected_services: list[str], severity: str = "partial") -> dict:
        window = {"id": f"mw-{len(self._windows) + 1}", "title": title,
                  "start": start, "end": end, "affected": affected_services,
                  "severity": severity, "status": "scheduled", "notes": []}
        self._windows.append(window)
        return {"id": window["id"], "title": title, "status": "scheduled"}

    def start_maintenance(self, window_id: str) -> dict:
        w = self._find(window_id)
        if not w:
            return {"error": "Window not found"}
        w["status"] = "in_progress"
        return {"id": window_id, "status": "in_progress"}

    def complete(self, window_id: str, *, notes: str = "") -> dict:
        w = self._find(window_id)
        if not w:
            return {"error": "Window not found"}
        w["status"] = "completed"
        if notes:
            w["notes"].append(notes)
        return {"id": window_id, "status": "completed"}

    def upcoming(self) -> list[dict]:
        return [w for w in self._windows if w["status"] == "scheduled"]

    def active(self) -> list[dict]:
        return [w for w in self._windows if w["status"] == "in_progress"]

    def _find(self, wid: str) -> dict | None:
        return next((w for w in self._windows if w["id"] == wid), None)
