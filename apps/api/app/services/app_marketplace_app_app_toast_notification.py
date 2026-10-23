"""Toast notification — generate ephemeral toast messages."""

import secrets


TOAST_TYPES = {
    "success": {"icon": "✅", "color": "green", "duration_ms": 3000},
    "error": {"icon": "❌", "color": "red", "duration_ms": 5000},
    "warning": {"icon": "⚠️", "color": "yellow", "duration_ms": 4000},
    "info": {"icon": "ℹ️", "color": "blue", "duration_ms": 3000},
}


def create_toast(*, message: str, toast_type: str = "info",
                   action_label: str | None = None) -> dict:
    config = TOAST_TYPES.get(toast_type, TOAST_TYPES["info"])
    return {
        "toast_id": f"toast_{secrets.token_urlsafe(6)}",
        "message": message,
        "type": toast_type,
        **config,
        "action_label": action_label,
        "dismissible": True,
    }
