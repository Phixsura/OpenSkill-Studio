"""Toast notification system — transient UI notifications with auto-dismiss."""
from __future__ import annotations
import secrets


VARIANTS = {
    "success": {"icon": "✅", "color": "green", "default_duration": 3000},
    "error": {"icon": "❌", "color": "red", "default_duration": 5000},
    "warning": {"icon": "⚠️", "color": "yellow", "default_duration": 4000},
    "info": {"icon": "ℹ️", "color": "blue", "default_duration": 3000},
}


def create_toast(*, title: str, message: str = "", variant: str = "info",
                   duration_ms: int | None = None, action: dict | None = None) -> dict:
    v = VARIANTS.get(variant, VARIANTS["info"])
    return {
        "id": f"toast_{secrets.token_hex(4)}",
        "title": title, "message": message,
        "variant": variant, "icon": v["icon"], "color": v["color"],
        "duration_ms": duration_ms or v["default_duration"],
        "action": action,
        "dismissible": True,
    }


def create_batch(toasts: list[dict]) -> list[dict]:
    return [create_toast(**t) for t in toasts]
