"""App preview — generate preview links and share drafts before publishing."""

import hashlib
import secrets
from datetime import datetime, timezone, timedelta


def create_preview_link(*, app_id: str, version_id: str, expires_hours: int = 24) -> dict:
    token = secrets.token_urlsafe(24)
    expires = (datetime.now(timezone.utc) + timedelta(hours=expires_hours)).isoformat()
    return {"app_id": app_id, "version_id": version_id, "token": token,
            "url": f"https://preview.openskill.dev/{token}",
            "expires_at": expires, "views": 0, "max_views": 100}


def validate_preview_token(*, token: str, stored: dict) -> dict:
    if datetime.now(timezone.utc).isoformat() > stored.get("expires_at", ""):
        return {"valid": False, "reason": "Preview link expired"}
    if stored.get("views", 0) >= stored.get("max_views", 100):
        return {"valid": False, "reason": "View limit reached"}
    return {"valid": True, "reason": None}


def build_preview_page(*, app: dict, version: dict, is_preview: bool = True) -> dict:
    return {"app": app, "version": version, "is_preview": is_preview,
            "banner": "⚠️ This is a preview — not the published version" if is_preview else None,
            "actions_disabled": is_preview}
