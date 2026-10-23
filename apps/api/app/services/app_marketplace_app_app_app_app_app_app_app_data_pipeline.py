"""Data pipeline manager — define and run ETL pipelines."""
from __future__ import annotations
import time


def create_pipeline(name: str, steps: list[dict]) -> dict:
    return {"name": name, "steps": steps, "step_count": len(steps),
            "status": "idle", "created_at": time.time()}


def run_pipeline(pipeline: dict, input_data: list[dict]) -> dict:
    current = input_data
    results = []
    for step in pipeline["steps"]:
        action = step.get("action", "passthrough")
        if action == "filter":
            field, value = step.get("field", ""), step.get("value", "")
            current = [r for r in current if r.get(field) == value]
        elif action == "map":
            field = step.get("field", "")
            fn = step.get("transform", "upper")
            if fn == "upper" and field:
                current = [{**r, field: str(r.get(field, "")).upper()} for r in current]
        elif action == "sort":
            field = step.get("field", "")
            current = sorted(current, key=lambda r: r.get(field, ""))
        results.append({"step": step.get("name", action), "output_count": len(current)})
    return {"pipeline": pipeline["name"], "input_count": len(input_data),
            "output_count": len(current), "output": current,
            "step_results": results, "status": "completed"}
