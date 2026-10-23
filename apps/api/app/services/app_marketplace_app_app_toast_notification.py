"""Toast notification — ephemeral notification builder."""

import html
import secrets
from datetime import datetime, timezone

TYPES = {
    "success": {"icon": "✅", "color": "green"},
    "error": {"icon": "❌", "color": "red"},
    "warning": {"icon": "⚠️", "color": "yellow"},
    "info": {"icon": "ℹ️", "color": "blue"},
}


def create_toast(*, message: str, type: str = "info", duration_ms: int = 5000,
                   action_label: str | None = None) -> dict:
    info = TYPES.get(type, TYPES["info"])
    return {"id": f"toast_{secrets.token_hex(4)}", "message": html.escape(message),
            "type": type, "icon": info["icon"], "color": info["color"],
            "duration_ms": duration_ms, "action_label": html.escape(action_label) if action_label else None,
            "dismissible": True, "created_at": datetime.now(timezone.utc).isoformat()}


def build_toast_queue(*, toasts: list[dict], max_visible: int = 3) -> dict:
    visible = toasts[:max_visible]
    queued = toasts[max_visible:]
    return {"visible": visible, "queued": queued,
            "visible_count": len(visible), "queued_count": len(queued),
            "total": len(toasts)}
