"""Consumer API Webhook Audit Log — immutable webhook audit log with retention."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

AUDIT_ACTIONS = ("created", "updated", "deleted", "enabled", "disabled",
                 "secret_rotated", "url_changed", "delivered", "failed")


@dataclass
class AuditLogEntry:
    entry_id: str
    webhook_id: str
    action: str
    actor: str
    details: str = ""
    timestamp: float = 0.0


@dataclass
class WebhookAuditLog:
    """Immutable audit log for webhook lifecycle events."""

    _entries: list[AuditLogEntry] = field(default_factory=list)
    _max_entries: int = 50000

    def log(self, entry: AuditLogEntry) -> dict:
        if entry.action not in AUDIT_ACTIONS:
            raise ValueError(f"Invalid action: {entry.action}")
        if len(self._entries) >= self._max_entries:
            self._entries = self._entries[-(self._max_entries // 2):]
        self._entries.append(entry)
        logger.info("webhook_audit_logged", webhook_id=entry.webhook_id, action=entry.action)
        return {"entry_id": entry.entry_id, "action": entry.action}

    def query(self, webhook_id: str | None = None, action: str | None = None,
              actor: str | None = None, limit: int = 50) -> list[dict]:
        results = list(reversed(self._entries))
        if webhook_id:
            results = [e for e in results if e.webhook_id == webhook_id]
        if action:
            results = [e for e in results if e.action == action]
        if actor:
            results = [e for e in results if e.actor == actor]
        return [
            {"entry_id": e.entry_id, "webhook_id": e.webhook_id,
             "action": e.action, "actor": e.actor, "details": e.details,
             "timestamp": e.timestamp}
            for e in results[:limit]
        ]

    def get_webhook_history(self, webhook_id: str) -> list[dict]:
        return self.query(webhook_id=webhook_id, limit=100)

    def get_actor_activity(self, actor: str, limit: int = 20) -> list[dict]:
        return self.query(actor=actor, limit=limit)

    def get_stats(self) -> dict:
        by_action: dict[str, int] = {}
        webhooks: set[str] = set()
        actors: set[str] = set()
        for e in self._entries:
            by_action[e.action] = by_action.get(e.action, 0) + 1
            webhooks.add(e.webhook_id)
            actors.add(e.actor)
        return {
            "total_entries": len(self._entries),
            "unique_webhooks": len(webhooks),
            "unique_actors": len(actors),
            "by_action": by_action,
        }

    def count(self) -> int:
        return len(self._entries)
