"""Platform migration wizard — guide users through data migration steps."""
from __future__ import annotations


def create_migration(*, source: str, destination: str, data_types: list[str]) -> dict:
    steps = []
    for i, dt in enumerate(data_types):
        steps.append({"index": i, "data_type": dt, "status": "pending",
                       "records_migrated": 0, "errors": 0})
    return {
        "source": source, "destination": destination,
        "steps": steps, "total_steps": len(steps),
        "completed": 0, "status": "ready",
    }


def run_step(migration: dict, index: int, *, records: int, errors: int = 0) -> dict:
    if index >= len(migration["steps"]):
        return {"error": "Step index out of range"}
    step = migration["steps"][index]
    step["status"] = "completed" if errors == 0 else "completed_with_errors"
    step["records_migrated"] = records
    step["errors"] = errors
    migration["completed"] = sum(1 for s in migration["steps"]
                                  if s["status"].startswith("completed"))
    if migration["completed"] == migration["total_steps"]:
        migration["status"] = "completed"
    else:
        migration["status"] = "in_progress"
    total_records = sum(s["records_migrated"] for s in migration["steps"])
    total_errors = sum(s["errors"] for s in migration["steps"])
    return {"step": index, "data_type": step["data_type"],
            "records": records, "errors": errors,
            "total_records": total_records, "total_errors": total_errors,
            "progress": f"{migration['completed']}/{migration['total_steps']}"}
