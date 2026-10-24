"""Runbook executor — execute operational runbooks step by step."""
from __future__ import annotations


class RunbookExecutor:
    def __init__(self):
        self._runbooks: dict[str, dict] = {}

    def register(self, name: str, steps: list[dict], severity: str = "standard") -> dict:
        self._runbooks[name] = {"name": name, "steps": steps, "severity": severity}
        return {"name": name, "steps": len(steps)}

    def execute(self, name: str) -> dict:
        rb = self._runbooks.get(name)
        if not rb:
            return {"success": False, "error": "runbook_not_found"}
        results = []
        for i, step in enumerate(rb["steps"]):
            action = step.get("action")
            try:
                output = action() if action else {"skipped": True}
                results.append({"step": step["name"], "status": "success", "output": output})
            except Exception as e:
                results.append({"step": step["name"], "status": "failed", "error": str(e)})
                if step.get("critical", False):
                    return {"success": False, "steps": results, "stopped_at": i}
        return {"success": True, "steps": results, "completed": len(results)}

    def list_runbooks(self) -> list[dict]:
        return [{"name": r["name"], "steps": len(r["steps"]), "severity": r["severity"]}
                for r in self._runbooks.values()]
