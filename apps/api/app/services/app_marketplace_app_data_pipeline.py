"""Data pipeline — ETL pipeline management for app data processing."""

from datetime import datetime, timezone


def create_pipeline(*, app_id: str, name: str, source: dict, transforms: list[dict],
                      destination: dict) -> dict:
    if not source.get("type"):
        return {"error": "Source must specify a type"}
    return {"app_id": app_id, "name": name, "source": source,
            "transforms": transforms, "destination": destination,
            "transform_count": len(transforms), "status": "created", "error": None}


def execute_pipeline_step(*, step: dict, data: list[dict]) -> list[dict]:
    step_type = step.get("type")
    if step_type == "filter":
        field = step.get("field", "")
        value = step.get("value")
        return [d for d in data if d.get(field) == value]
    elif step_type == "map":
        field = step.get("field", "")
        rename = step.get("rename", field)
        return [{**d, rename: d.get(field)} for d in data]
    elif step_type == "aggregate":
        field = step.get("field", "")
        values = [d.get(field, 0) for d in data]
        return [{"count": len(values), "sum": sum(values), "avg": sum(values) / max(len(values), 1)}]
    return data


def get_pipeline_stats(*, runs: list[dict]) -> dict:
    if not runs:
        return {"total_runs": 0, "success_rate": 0, "avg_duration_ms": 0}
    successes = sum(1 for r in runs if r.get("status") == "success")
    return {"total_runs": len(runs),
            "success_rate": round(successes / len(runs) * 100, 1),
            "avg_duration_ms": round(sum(r.get("duration_ms", 0) for r in runs) / len(runs))}
