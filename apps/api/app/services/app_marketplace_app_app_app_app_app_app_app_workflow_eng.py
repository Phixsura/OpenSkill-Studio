"""Platform workflow engine — define and execute multi-step workflows."""
from __future__ import annotations


class WorkflowEngine:
    def __init__(self):
        self._workflows: dict[str, dict] = {}

    def define(self, name: str, steps: list[dict]) -> dict:
        self._workflows[name] = {"name": name, "steps": steps, "status": "defined"}
        return {"name": name, "steps": len(steps)}

    def execute(self, name: str, context: dict | None = None) -> dict:
        wf = self._workflows.get(name)
        if not wf:
            return {"success": False, "error": "workflow_not_found"}
        results = []
        ctx = dict(context or {})
        for i, step in enumerate(wf["steps"]):
            fn = step.get("fn")
            try:
                output = fn(ctx) if fn else {"ok": True}
                ctx.update(output if isinstance(output, dict) else {})
                results.append({"step": step["name"], "status": "success", "output": output})
            except Exception as e:
                results.append({"step": step["name"], "status": "failed", "error": str(e)})
                return {"success": False, "steps": results, "failed_at": i}
        return {"success": True, "steps": results, "context": ctx}

    def list(self) -> list[dict]:
        return [{"name": w["name"], "steps": len(w["steps"])} for w in self._workflows.values()]
