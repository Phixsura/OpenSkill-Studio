"""Platform announcements — manage system-wide announcements for developers."""

from datetime import datetime, timezone

def create_announcement(*, title: str, body: str, type: str = "info", pinned: bool = False) -> dict:
    valid_types = {"info", "warning", "critical", "feature"}
    if type not in valid_types:
        return {"error": f"Invalid type: {type}"}
    return {"title": title, "body": body, "type": type, "pinned": pinned,
            "created_at": datetime.now(timezone.utc).isoformat(), "error": None}

def get_active_announcements(*, announcements: list[dict]) -> list[dict]:
    pinned = [a for a in announcements if a.get("pinned")]
    regular = [a for a in announcements if not a.get("pinned")]
    return pinned + regular
