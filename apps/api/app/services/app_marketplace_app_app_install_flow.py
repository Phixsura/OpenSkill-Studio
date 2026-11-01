"""App install flow — multi-step guided installation process."""

import secrets
from datetime import datetime


def start_install(*, app_id: str, app_name: str, user_id: str,
                    permissions: list[str]) -> dict:
    return {
        "install_id": f"inst_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "app_name": app_name,
        "user_id": user_id,
        "permissions_requested": permissions,
        "steps": [
            {"id": "review_permissions", "label": "Review Permissions", "status": "current"},
            {"id": "configure", "label": "Configure Settings", "status": "pending"},
            {"id": "connect", "label": "Connect Account", "status": "pending"},
            {"id": "complete", "label": "Ready to Use", "status": "pending"},
        ],
        "status": "in_progress",
        "started_at": datetime.utcnow().isoformat(),
    }


def complete_step(*, install: dict, step_id: str) -> dict:
    steps = install.get("steps", [])
    found = False
    for i, step in enumerate(steps):
        if step["id"] == step_id:
            step["status"] = "completed"
            found = True
            if i + 1 < len(steps):
                steps[i + 1]["status"] = "current"
    if not found:
        return {"error": f"Step not found: {step_id}"}
    all_done = all(s["status"] == "completed" for s in steps)
    return {**install, "steps": steps,
            "status": "completed" if all_done else "in_progress"}
