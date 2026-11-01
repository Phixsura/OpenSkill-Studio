"""Notification center — unified in-app notifications with read/unread tracking."""
from __future__ import annotations
import secrets
import time
import html


class NotificationCenter:
    def __init__(self):
        self._notifications: dict[str, list[dict]] = {}

    def send(self, *, user_id: str, title: str, body: str = "",
              category: str = "info", link: str = "") -> dict:
        nid = f"notif_{secrets.token_hex(6)}"
        notif = {"id": nid, "title": html.escape(title),
                 "body": html.escape(body[:500]), "category": category,
                 "link": link, "read": False, "created": time.time()}
        self._notifications.setdefault(user_id, []).append(notif)
        return {"id": nid, "sent": True}

    def get_unread(self, user_id: str) -> list[dict]:
        return [n for n in self._notifications.get(user_id, []) if not n["read"]]

    def mark_read(self, user_id: str, notif_id: str) -> dict:
        for n in self._notifications.get(user_id, []):
            if n["id"] == notif_id:
                n["read"] = True
                return {"marked": True}
        return {"error": "Not found"}

    def mark_all_read(self, user_id: str) -> dict:
        count = 0
        for n in self._notifications.get(user_id, []):
            if not n["read"]:
                n["read"] = True
                count += 1
        return {"marked": count}

    def unread_count(self, user_id: str) -> int:
        return len(self.get_unread(user_id))
