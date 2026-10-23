"""Runbook executor — define and execute operational runbooks step by step."""
from __future__ import annotations


def create_runbook(*, name: str, steps: list[dict], tags: list[str] | None = None) -> dict:
    return {
        "name": name, "tags": tags or [],
        "steps": [{"index": i, "title": s.get("title", ""), "command": s.get("command", ""),
                    "expected": s.get("expected", ""), "status": "pending", "output": ""}
                   for i, s in enumerate(steps)],
        "total_steps": len(steps), "completed": 0, "status": "ready",
    }


def execute_step(runbook: dict, index: int, *, output: str = "", success: bool = True) -> dict:
    if index >= len(runbook["steps"]):
        return {"error": "Step index out of range"}
    step = runbook["steps"][index]
    step["status"] = "passed" if success else "failed"
    step["output"] = output
    runbook["completed"] = sum(1 for s in runbook["steps"] if s["status"] == "passed")
    if any(s["status"] == "failed" for s in runbook["steps"]):
        runbook["status"] = "failed"
    elif runbook["completed"] == runbook["total_steps"]:
        runbook["status"] = "completed"
    else:
        runbook["status"] = "in_progress"
    return {"step": index, "title": step["title"], "status": step["status"],
            "runbook_status": runbook["status"],
            "progress": f"{runbook['completed']}/{runbook['total_steps']}"}
