"""Playground sandbox — interactive code sandbox for trying apps."""

import secrets
from datetime import datetime, timedelta


def create_sandbox(*, app_id: str, user_id: str, template: str = "default",
                     timeout_min: int = 30) -> dict:
    valid_templates = {"default", "react", "node", "python", "fullstack"}
    if template not in valid_templates:
        return {"error": f"Invalid template. Valid: {', '.join(sorted(valid_templates))}"}
    if timeout_min > 120:
        return {"error": "Max timeout is 120 minutes"}
    sandbox_id = f"sb_{secrets.token_urlsafe(8)}"
    return {
        "sandbox_id": sandbox_id,
        "app_id": app_id,
        "user_id": user_id,
        "template": template,
        "status": "running",
        "url": f"https://sandbox.openskill.dev/{sandbox_id}",
        "expires_at": (datetime.utcnow() + timedelta(minutes=timeout_min)).isoformat(),
        "resources": {"cpu": "0.5 vCPU", "memory": "512 MB", "storage": "1 GB"},
    }


def list_active_sandboxes(*, user_id: str) -> dict:
    return {
        "user_id": user_id,
        "sandboxes": [
            {"sandbox_id": "sb_1", "app_id": "app1", "template": "react",
             "status": "running", "created_at": "2026-10-23T12:00:00"},
        ],
        "total": 1,
        "max_concurrent": 3,
    }
