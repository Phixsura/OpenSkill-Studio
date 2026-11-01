"""Extension Admin Console — platform admin operations."""
from __future__ import annotations
from dataclasses import dataclass
import time


@dataclass
class AdminAction:
    action_id: str
    admin_id: str
    action: str
    target_type: str  # extension, developer, review, user
    target_id: str
    reason: str = ""
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


class ExtAdminConsoleService:
    VALID_ACTIONS = frozenset([
        "suspend_extension", "unsuspend_extension", "ban_developer",
        "unban_developer", "remove_review", "feature_extension",
        "unfeature_extension", "approve_extension", "reject_extension",
    ])

    def __init__(self):
        self._log: list[AdminAction] = []
        self._suspended: set[str] = set()
        self._banned: set[str] = set()
        self._featured: set[str] = set()
        self._counter = 0

    def execute(self, admin_id: str, action: str, target_type: str,
                target_id: str, reason: str = "") -> AdminAction:
        if action not in self.VALID_ACTIONS:
            raise ValueError(f"Invalid action: {action}")
        if not reason and action in ("suspend_extension", "ban_developer", "remove_review", "reject_extension"):
            raise ValueError("Reason required for this action")
        self._counter += 1
        entry = AdminAction(action_id=f"adm-{self._counter}", admin_id=admin_id,
                            action=action, target_type=target_type,
                            target_id=target_id, reason=reason)
        self._log.append(entry)
        # Apply
        if action == "suspend_extension": self._suspended.add(target_id)
        elif action == "unsuspend_extension": self._suspended.discard(target_id)
        elif action == "ban_developer": self._banned.add(target_id)
        elif action == "unban_developer": self._banned.discard(target_id)
        elif action == "feature_extension": self._featured.add(target_id)
        elif action == "unfeature_extension": self._featured.discard(target_id)
        return entry

    def is_suspended(self, extension_id: str) -> bool:
        return extension_id in self._suspended

    def is_banned(self, developer_id: str) -> bool:
        return developer_id in self._banned

    def get_featured(self) -> set[str]:
        return set(self._featured)

    def get_audit_log(self, limit: int = 100) -> list[AdminAction]:
        return list(reversed(self._log))[:limit]
