"""Progress tracker — multi-step progress with completion percentage."""
from __future__ import annotations


def create_progress(*, title: str, steps: list[str]) -> dict:
    return {
        "title": title,
        "steps": [{"index": i, "label": s, "completed": False} for i, s in enumerate(steps)],
        "total": len(steps), "completed": 0, "pct": 0,
    }


def complete_step(progress: dict, index: int) -> dict:
    if index >= len(progress["steps"]):
        return {"error": "Step index out of range"}
    progress["steps"][index]["completed"] = True
    done = sum(1 for s in progress["steps"] if s["completed"])
    progress["completed"] = done
    progress["pct"] = round(done / progress["total"] * 100)
    return {"step": index, "label": progress["steps"][index]["label"],
            "completed_count": done, "pct": progress["pct"],
            "finished": done == progress["total"]}


def get_next_step(progress: dict) -> dict | None:
    for s in progress["steps"]:
        if not s["completed"]:
            return s
    return None
