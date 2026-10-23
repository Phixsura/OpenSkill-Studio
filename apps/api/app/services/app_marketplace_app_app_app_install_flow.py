"""App install flow — multi-step app installation process."""

import html
import secrets
from datetime import datetime, timezone

INSTALL_STEPS = [
    {"id": "permissions", "label": "Review Permissions", "icon": "🔐"},
    {"id": "configure", "label": "Configure Settings", "icon": "⚙️"},
    {"id": "connect", "label": "Connect Accounts", "icon": "🔗"},
    {"id": "confirm", "label": "Confirm & Install", "icon": "✅"},
]


def start_install(*, app_id: str, app_name: str, permissions: list[str]) -> dict:
    install_id = f"inst_{secrets.token_hex(8)}"
    return {
        "install_id": install_id,
        "app_id": app_id,
        "app_name": html.escape(app_name),
        "permissions": permissions,
        "steps": INSTALL_STEPS,
        "current_step": 0,
        "total_steps": len(INSTALL_STEPS),
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def complete_install(*, install_id: str, app_id: str) -> dict:
    return {
        "install_id": install_id,
        "app_id": app_id,
        "status": "installed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "message": "App installed successfully! 🎉",
    }
