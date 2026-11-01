"""Extension Lifecycle Manager — manage the full lifecycle of extensions.

Handles extension submission, review, approval, publishing, updates,
and deprecation through a state machine with audit trail.
"""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum


class LifecycleState(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


VALID_TRANSITIONS: dict[LifecycleState, list[LifecycleState]] = {
    LifecycleState.DRAFT: [LifecycleState.SUBMITTED],
    LifecycleState.SUBMITTED: [LifecycleState.IN_REVIEW, LifecycleState.REJECTED],
    LifecycleState.IN_REVIEW: [LifecycleState.APPROVED, LifecycleState.REJECTED],
    LifecycleState.APPROVED: [LifecycleState.PUBLISHED],
    LifecycleState.PUBLISHED: [LifecycleState.SUSPENDED, LifecycleState.DEPRECATED],
    LifecycleState.SUSPENDED: [LifecycleState.PUBLISHED, LifecycleState.DEPRECATED],
    LifecycleState.DEPRECATED: [],
    LifecycleState.REJECTED: [LifecycleState.DRAFT],
}


class ExtensionLifecycle:
    """State machine for extension lifecycle with audit trail."""

    def __init__(self):
        self._extensions: dict[str, dict] = {}

    def create(self, extension_id: str, name: str, developer_id: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        ext = {
            "extension_id": extension_id,
            "name": name,
            "developer_id": developer_id,
            "state": LifecycleState.DRAFT,
            "created_at": now,
            "updated_at": now,
            "audit_log": [{"action": "created", "state": "draft", "at": now, "by": developer_id}],
        }
        self._extensions[extension_id] = ext
        return ext

    def transition(self, extension_id: str, target_state: LifecycleState, actor: str,
                   reason: str = "") -> tuple[bool, str]:
        """Attempt a state transition. Returns (success, message)."""
        ext = self._extensions.get(extension_id)
        if not ext:
            return False, "Extension not found"

        current = LifecycleState(ext["state"])
        allowed = VALID_TRANSITIONS.get(current, [])
        if target_state not in allowed:
            return False, f"Cannot transition from {current.value} to {target_state.value}"

        now = datetime.now(timezone.utc).isoformat()
        ext["state"] = target_state
        ext["updated_at"] = now
        ext["audit_log"].append({
            "action": f"{current.value} -> {target_state.value}",
            "state": target_state.value,
            "at": now,
            "by": actor,
            "reason": reason,
        })
        return True, f"Transitioned to {target_state.value}"

    def get_state(self, extension_id: str) -> LifecycleState | None:
        ext = self._extensions.get(extension_id)
        return LifecycleState(ext["state"]) if ext else None

    def get_audit_log(self, extension_id: str) -> list[dict]:
        ext = self._extensions.get(extension_id)
        return list(ext["audit_log"]) if ext else []

    def list_by_state(self, state: LifecycleState) -> list[dict]:
        return [e for e in self._extensions.values() if e["state"] == state]

    def submit(self, extension_id: str, developer_id: str) -> tuple[bool, str]:
        return self.transition(extension_id, LifecycleState.SUBMITTED, developer_id)

    def approve(self, extension_id: str, reviewer_id: str, reason: str = "") -> tuple[bool, str]:
        ok, msg = self.transition(extension_id, LifecycleState.IN_REVIEW, reviewer_id)
        if not ok:
            return ok, msg
        return self.transition(extension_id, LifecycleState.APPROVED, reviewer_id, reason)

    def publish(self, extension_id: str, actor: str) -> tuple[bool, str]:
        return self.transition(extension_id, LifecycleState.PUBLISHED, actor)

    def reject(self, extension_id: str, reviewer_id: str, reason: str) -> tuple[bool, str]:
        ext = self._extensions.get(extension_id)
        if not ext:
            return False, "Extension not found"
        current = LifecycleState(ext["state"])
        if current in (LifecycleState.SUBMITTED, LifecycleState.IN_REVIEW):
            return self.transition(extension_id, LifecycleState.REJECTED, reviewer_id, reason)
        return False, f"Cannot reject from {current.value}"
