"""Feature announcement — in-app feature announcements and what's new."""

import secrets
from datetime import datetime


def create_announcement(*, title: str, body: str, feature_tag: str,
                          cta_label: str | None = None, cta_url: str | None = None) -> dict:
    return {
        "announcement_id": f"ann_{secrets.token_urlsafe(8)}",
        "title": title,
        "body": body,
        "feature_tag": feature_tag,
        "cta": {"label": cta_label, "url": cta_url} if cta_label else None,
        "published_at": datetime.utcnow().isoformat(),
        "read_count": 0,
        "dismissed_count": 0,
    }


def get_whats_new(*, announcements: list[dict], last_seen: str | None = None) -> dict:
    if last_seen:
        new_items = [a for a in announcements if a.get("published_at", "") > last_seen]
    else:
        new_items = announcements
    return {
        "announcements": new_items[:10],
        "new_count": len(new_items),
        "has_unread": len(new_items) > 0,
    }
