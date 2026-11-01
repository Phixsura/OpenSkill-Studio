"""Data pipeline — ETL pipeline for app analytics data."""

import secrets
from datetime import datetime


def create_pipeline(*, name: str, source: dict, transforms: list[dict],
                      destination: dict, schedule: str | None = None) -> dict:
    if not source.get("type"):
        return {"error": "Source type is required"}
    if not destination.get("type"):
        return {"error": "Destination type is required"}
    return {
        "pipeline_id": f"dp_{secrets.token_urlsafe(8)}",
        "name": name,
        "source": source,
        "transforms": [{"step": i + 1, **t} for i, t in enumerate(transforms)],
        "destination": destination,
        "schedule": schedule,
        "status": "active" if schedule else "manual",
        "created_at": datetime.utcnow().isoformat(),
    }


def estimate_pipeline_cost(*, rows_per_day: int, transforms: int,
                              storage_gb: float) -> dict:
    compute_cost = round(rows_per_day / 1_000_000 * 0.05 * (1 + transforms * 0.1), 2)
    storage_cost = round(storage_gb * 0.023, 2)
    total = round(compute_cost + storage_cost, 2)
    return {
        "compute_cost_per_day": compute_cost,
        "storage_cost_per_day": storage_cost,
        "total_daily": total,
        "estimated_monthly": round(total * 30, 2),
    }
