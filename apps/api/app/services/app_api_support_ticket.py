"""App API Support Ticket — manage developer support tickets.

Manages support tickets:
- Create tickets with priority
- Track status lifecycle
- Assign to support agents
- Per-installation scoped tickets
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class SupportTicket:
    """A developer support ticket."""

    ticket_id: str
    subject: str
    submitter: str
    priority: TicketPriority
    status: TicketStatus = TicketStatus.OPEN
    assignee: str = ""
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None


class AppAPISupportTicket:
    """Manage developer support tickets."""

    def __init__(self) -> None:
        self._tickets: dict[tuple[str, str], SupportTicket] = {}

    def create(
        self, installation_id: str, ticket_id: str, subject: str,
        submitter: str, priority: TicketPriority,
    ) -> SupportTicket:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, ticket_id)
        if key in self._tickets:
            raise ValueError(f"Ticket {ticket_id} already exists")

        ticket = SupportTicket(
            ticket_id=ticket_id, subject=subject,
            submitter=submitter, priority=priority,
        )
        self._tickets[key] = ticket
        return ticket

    def assign(self, installation_id: str, ticket_id: str, assignee: str) -> SupportTicket:
        t = self._get(installation_id, ticket_id)
        t.assignee = assignee
        t.status = TicketStatus.IN_PROGRESS
        return t

    def resolve(self, installation_id: str, ticket_id: str) -> SupportTicket:
        t = self._get(installation_id, ticket_id)
        t.status = TicketStatus.RESOLVED
        t.resolved_at = time.time()
        return t

    def open_tickets(self, installation_id: str) -> list[SupportTicket]:
        return [t for (inst, _), t in self._tickets.items() if inst == installation_id and t.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED)]

    def list_tickets(self, installation_id: str) -> list[SupportTicket]:
        return [t for (inst, _), t in self._tickets.items() if inst == installation_id]

    def _get(self, installation_id: str, ticket_id: str) -> SupportTicket:
        key = (installation_id, ticket_id)
        t = self._tickets.get(key)
        if t is None:
            raise KeyError(f"Ticket {ticket_id} not found")
        return t
