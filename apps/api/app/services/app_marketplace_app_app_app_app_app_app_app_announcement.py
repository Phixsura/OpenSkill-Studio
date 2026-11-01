"""Announcement banner — platform-wide announcements with dismissal tracking."""
from __future__ import annotations
import html
import secrets


class AnnouncementManager:
    def __init__(self):
        self._announcements: list[dict] = []
        self._dismissed: dict[str, set[str]] = {}

    def create(self, *, title: str, body: str = "", variant: str = "info",
                link: str = "", dismissible: bool = True) -> dict:
        aid = f"ann_{secrets.token_hex(4)}"
        self._announcements.append({
            "id": aid, "title": html.escape(title), "body": html.escape(body[:300]),
            "variant": variant, "link": link, "dismissible": dismissible, "active": True,
        })
        return {"id": aid, "title": html.escape(title)}

    def dismiss(self, announcement_id: str, user_id: str) -> dict:
        self._dismissed.setdefault(user_id, set()).add(announcement_id)
        return {"dismissed": True}

    def get_active(self, *, user_id: str = "") -> list[dict]:
        dismissed = self._dismissed.get(user_id, set())
        return [a for a in self._announcements if a["active"] and a["id"] not in dismissed]

    def deactivate(self, announcement_id: str) -> dict:
        for a in self._announcements:
            if a["id"] == announcement_id:
                a["active"] = False
                return {"deactivated": True}
        return {"error": "Not found"}
