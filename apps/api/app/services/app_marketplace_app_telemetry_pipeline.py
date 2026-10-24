"""Telemetry pipeline — ingest, process, and route telemetry data."""

import secrets
from datetime import datetime


SIGNAL_TYPES = {"traces", "metrics", "logs"}


def create_pipeline(*, app_id: str, name: str, sources: list[str],
                      destinations: list[str], filters: list[dict] | None = None) -> dict:
    if not sources:
        return {"error": "At least one source is required"}
    if not destinations:
        return {"error": "At least one destination is required"}
    return {
        "pipeline_id": f"pipe_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "name": name,
        "sources": sources,
        "destinations": destinations,
        "filters": filters or [],
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }


def estimate_data_volume(*, events_per_sec: int, avg_event_bytes: int = 512,
                           retention_days: int = 30) -> dict:
    daily_bytes = events_per_sec * avg_event_bytes * 86400
    daily_gb = round(daily_bytes / (1024 ** 3), 2)
    total_gb = round(daily_gb * retention_days, 2)
    monthly_cost = round(total_gb * 0.25, 2)  # $0.25/GB
    return {
        "events_per_sec": events_per_sec,
        "daily_volume_gb": daily_gb,
        "total_volume_gb": total_gb,
        "retention_days": retention_days,
        "estimated_monthly_cost": monthly_cost,
    }
