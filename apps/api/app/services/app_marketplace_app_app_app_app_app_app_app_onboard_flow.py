"""Onboarding flow engine — guide users through setup steps."""
from __future__ import annotations


def create_flow(steps: list[dict]) -> dict:
    items = []
    for i, s in enumerate(steps):
        items.append({"index": i, "title": s.get("title", ""),
                       "description": s.get("description", ""),
                       "required": s.get("required", True),
                       "completed": False})
    return {"steps": items, "total": len(items),
            "completed": 0, "progress_pct": 0}


def complete_step(flow: dict, step_index: int) -> dict:
    if step_index >= len(flow["steps"]):
        return {"completed": False, "error": "invalid_step"}
    flow["steps"][step_index]["completed"] = True
    done = sum(1 for s in flow["steps"] if s["completed"])
    flow["completed"] = done
    flow["progress_pct"] = round(done / flow["total"] * 100)
    required_done = all(s["completed"] for s in flow["steps"] if s["required"])
    return {"completed": True, "step": step_index, "progress_pct": flow["progress_pct"],
            "all_required_done": required_done, "flow_complete": done == flow["total"]}


def skip_step(flow: dict, step_index: int) -> dict:
    if step_index >= len(flow["steps"]):
        return {"skipped": False, "error": "invalid_step"}
    step = flow["steps"][step_index]
    if step["required"]:
        return {"skipped": False, "error": "cannot_skip_required"}
    step["completed"] = True
    flow["completed"] = sum(1 for s in flow["steps"] if s["completed"])
    flow["progress_pct"] = round(flow["completed"] / flow["total"] * 100)
    return {"skipped": True, "step": step_index}
