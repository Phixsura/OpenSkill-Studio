"""App API Developer Support Ticket — developer support ticket management."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class SupportTicket:
    ticket_id: str
    developer_id: str
    subject: str
    description: str
    priority: str  # "low", "normal", "high", "urgent"
    status: str = "open"  # "open", "in_progress", "waiting", "resolved", "closed"
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None

    @property
    def resolution_time_hours(self) -> float | None:
        if self.resolved_at is None: return None
        return round((self.resolved_at - self.created_at) / 3600, 1)

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicket:
    def __init__(self) -> None:
        self._tickets: dict[tuple[str, str], SupportTicket] = {}

    def create(self, installation_id: str, ticket_id: str, developer_id: str, subject: str, description: str, priority: str = "normal") -> SupportTicket:
        if not installation_id: raise ValueError("installation_id is required")
        if priority not in ("low", "normal", "high", "urgent"): raise ValueError("invalid priority")
        key = (installation_id, ticket_id)
        if key in self._tickets: raise ValueError(f"Ticket {ticket_id} exists")
        t = SupportTicket(ticket_id=ticket_id, developer_id=developer_id, subject=subject, description=description, priority=priority)
        self._tickets[key] = t
        return t

    def update_status(self, installation_id: str, ticket_id: str, status: str) -> SupportTicket:
        valid = {"open", "in_progress", "waiting", "resolved", "closed"}
        if status not in valid: raise ValueError("invalid status")
        t = self._get(installation_id, ticket_id)
        t.status = status
        if status in ("resolved", "closed"): t.resolved_at = time.time()
        return t

    def open_tickets(self, installation_id: str) -> list[SupportTicket]:
        return [t for (inst, _), t in self._tickets.items() if inst == installation_id and t.status in ("open", "in_progress", "waiting")]

    def avg_resolution_hours(self, installation_id: str) -> float:
        resolved = [t for (inst, _), t in self._tickets.items() if inst == installation_id and t.resolution_time_hours is not None]
        if not resolved: return 0.0
        return round(sum(t.resolution_time_hours for t in resolved) / len(resolved), 1)

    def by_priority(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), t in self._tickets.items():
            if inst == installation_id: counts[t.priority] = counts.get(t.priority, 0) + 1
        return counts

    def _get(self, installation_id: str, ticket_id: str) -> SupportTicket:
        key = (installation_id, ticket_id)
        t = self._tickets.get(key)
        if t is None: raise KeyError(f"Ticket {ticket_id} not found")
        return t
