"""Workflow automation engine — define and execute multi-step workflows."""
from __future__ import annotations
import secrets


class WorkflowEngine:
    def __init__(self):
        self._workflows: dict[str, dict] = {}

    def create(self, *, name: str, trigger: str, steps: list[dict]) -> dict:
        wid = f"wf_{secrets.token_hex(6)}"
        self._workflows[wid] = {
            "id": wid, "name": name, "trigger": trigger, "enabled": True,
            "steps": [{"index": i, "action": s["action"], "config": s.get("config", {}),
                        "status": "pending"} for i, s in enumerate(steps)],
            "runs": 0, "last_status": None,
        }
        return {"id": wid, "name": name, "steps": len(steps)}

    def execute(self, wid: str) -> dict:
        wf = self._workflows.get(wid)
        if not wf:
            return {"error": "Workflow not found"}
        if not wf["enabled"]:
            return {"error": "Workflow disabled"}
        wf["runs"] += 1
        all_ok = True
        for step in wf["steps"]:
            step["status"] = "completed"  # simplified execution
        wf["last_status"] = "success" if all_ok else "failed"
        return {"id": wid, "status": wf["last_status"], "runs": wf["runs"],
                "steps_executed": len(wf["steps"])}

    def toggle(self, wid: str) -> dict:
        wf = self._workflows.get(wid)
        if not wf:
            return {"error": "Workflow not found"}
        wf["enabled"] = not wf["enabled"]
        return {"id": wid, "enabled": wf["enabled"]}

    def list_workflows(self) -> list[dict]:
        return [{"id": w["id"], "name": w["name"], "trigger": w["trigger"],
                 "enabled": w["enabled"], "steps": len(w["steps"]),
                 "runs": w["runs"], "last_status": w["last_status"]}
                for w in self._workflows.values()]
