"""Rollback manager — safely roll back app deployments."""

import secrets
from datetime import datetime


def create_rollback(*, app_id: str, from_version: str, to_version: str,
                      reason: str) -> dict:
    return {
        "rollback_id": f"rb_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "from_version": from_version,
        "to_version": to_version,
        "reason": reason,
        "status": "pending",
        "steps": [
            {"name": "stop_traffic", "status": "pending"},
            {"name": "swap_version", "status": "pending"},
            {"name": "health_check", "status": "pending"},
            {"name": "resume_traffic", "status": "pending"},
        ],
        "created_at": datetime.utcnow().isoformat(),
        "estimated_time_sec": 120,
    }


def get_rollback_history(*, app_id: str) -> dict:
    return {
        "app_id": app_id,
        "rollbacks": [
            {"rollback_id": "rb_1", "from_version": "2.1.0", "to_version": "2.0.5",
             "reason": "High error rate", "status": "completed", "duration_sec": 95,
             "created_at": "2026-10-20T14:00:00"},
        ],
        "total": 1,
    }
