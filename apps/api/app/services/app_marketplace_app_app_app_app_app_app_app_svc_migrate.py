"""Service migration tracker — track service migrations between platforms."""
from __future__ import annotations


class ServiceMigrationTracker:
    def __init__(self):
        self._migrations: dict[str, dict] = {}

    def start(self, service: str, from_platform: str, to_platform: str) -> dict:
        self._migrations[service] = {"service": service, "from": from_platform,
                                      "to": to_platform, "status": "planning",
                                      "steps_completed": 0, "total_steps": 0}
        return self._migrations[service]

    def set_steps(self, service: str, steps: list[str]) -> dict:
        m = self._migrations[service]
        m["total_steps"] = len(steps)
        m["steps"] = steps
        return {"service": service, "total_steps": len(steps)}

    def complete_step(self, service: str) -> dict:
        m = self._migrations[service]
        m["steps_completed"] += 1
        if m["steps_completed"] >= m["total_steps"]:
            m["status"] = "completed"
        else:
            m["status"] = "in_progress"
        pct = round(m["steps_completed"] / max(m["total_steps"], 1) * 100)
        return {"service": service, "status": m["status"], "progress_pct": pct}

    def summary(self) -> dict:
        completed = sum(1 for m in self._migrations.values() if m["status"] == "completed")
        in_progress = sum(1 for m in self._migrations.values() if m["status"] == "in_progress")
        return {"total": len(self._migrations), "completed": completed,
                "in_progress": in_progress, "planning": len(self._migrations) - completed - in_progress}
