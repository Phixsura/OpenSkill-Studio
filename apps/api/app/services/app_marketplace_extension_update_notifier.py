"""Extension Update Notifier — notify users when installed extensions update."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class UpdateNotification:
    notif_id: str
    extension_id: str
    old_version: str
    new_version: str
    changelog: list[str] = field(default_factory=list)
    breaking: bool = False
    notified_users: set[str] = field(default_factory=set)
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtUpdateNotifierService:
    def __init__(self):
        self._notifications: list[UpdateNotification] = []
        self._subscriptions: dict[str, set[str]] = {}  # ext_id -> user_ids
        self._counter = 0

    def subscribe(self, user_id: str, extension_id: str) -> None:
        if extension_id not in self._subscriptions:
            self._subscriptions[extension_id] = set()
        self._subscriptions[extension_id].add(user_id)

    def unsubscribe(self, user_id: str, extension_id: str) -> bool:
        subs = self._subscriptions.get(extension_id)
        if subs and user_id in subs:
            subs.discard(user_id)
            return True
        return False

    def publish_update(self, extension_id: str, old_ver: str, new_ver: str,
                       changelog: list[str], breaking: bool = False) -> UpdateNotification:
        self._counter += 1
        subscribers = self._subscriptions.get(extension_id, set())
        notif = UpdateNotification(
            notif_id=f"upd-{self._counter}", extension_id=extension_id,
            old_version=old_ver, new_version=new_ver,
            changelog=changelog, breaking=breaking,
            notified_users=set(subscribers))
        self._notifications.append(notif)
        return notif

    def get_user_updates(self, user_id: str, unread_only: bool = False) -> list[UpdateNotification]:
        return [n for n in self._notifications if user_id in n.notified_users]

    def get_breaking_updates(self, user_id: str) -> list[UpdateNotification]:
        return [n for n in self.get_user_updates(user_id) if n.breaking]
