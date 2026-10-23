"""Runbook executor — define and execute operational runbooks."""
from __future__ import annotations
import time


def create_runbook(name: str, steps: list[dict], author: str = "") -> dict:
    items = []
    for i, s in enumerate(steps):
        items.append({"index": i, "title": s.get("title", f"Step {i+1}"),
                       "description": s.get("description", ""),
                       "type": s.get("type", "manual"),
                       "status": "pending"})
    return {"name": name, "author": author, "steps": items,
            "total_steps": len(items), "created_at": time.time()}


def execute_step(runbook: dict, step_index: int, result: str = "success") -> dict:
    if step_index >= len(runbook["steps"]):
        return {"executed": False, "error": "invalid_step"}
    step = runbook["steps"][step_index]
    step["status"] = result
    completed = sum(1 for s in runbook["steps"] if s["status"] in ("success", "skipped"))
    failed = sum(1 for s in runbook["steps"] if s["status"] == "failed")
    return {"executed": True, "step": step["title"], "result": result,
            "completed": completed, "total": runbook["total_steps"],
            "progress_pct": round(completed / runbook["total_steps"] * 100),
            "has_failures": failed > 0}


def runbook_status(runbook: dict) -> dict:
    completed = sum(1 for s in runbook["steps"] if s["status"] != "pending")
    failed = sum(1 for s in runbook["steps"] if s["status"] == "failed")
    status = "complete" if completed == runbook["total_steps"] else "in_progress" if completed > 0 else "not_started"
    return {"name": runbook["name"], "status": status, "completed": completed,
            "total": runbook["total_steps"], "failed": failed}
