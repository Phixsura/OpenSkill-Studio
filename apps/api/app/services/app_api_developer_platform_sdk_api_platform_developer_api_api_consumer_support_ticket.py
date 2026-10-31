"""API Consumer Support Ticket — track consumer support requests."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
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
    WAITING = "waiting_on_consumer"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class SupportTicket:
    ticket_id: str
    consumer_id: str
    subject: str
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    category: str = "general"  # "general", "bug", "integration", "billing", "security"
    created_at: float = field(default_factory=time.time)
    resolved_at: float = 0.0

VALID_CATEGORIES = {"general", "bug", "integration", "billing", "security", "feature_request"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicket:
    def __init__(self) -> None:
        self._tickets: dict[tuple[str, str], SupportTicket] = {}

    def create_ticket(self, installation_id: str, ticket: SupportTicket) -> SupportTicket:
        if not installation_id: raise ValueError("installation_id is required")
        if not ticket.subject: raise ValueError("subject is required")
        if ticket.category not in VALID_CATEGORIES: raise ValueError(f"Invalid category: {ticket.category}")
        key = (installation_id, ticket.ticket_id)
        if key in self._tickets: raise ValueError(f"Ticket {ticket.ticket_id} exists")
        self._tickets[key] = ticket
        return ticket

    def update_status(self, installation_id: str, ticket_id: str, status: TicketStatus) -> SupportTicket:
        t = self._get(installation_id, ticket_id)
        t.status = status
        if status == TicketStatus.RESOLVED: t.resolved_at = time.time()
        return t

    def open_tickets(self, installation_id: str, consumer_id: str | None = None) -> list[SupportTicket]:
        tickets = [t for (inst, _), t in self._tickets.items() if inst == installation_id and t.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED)]
        if consumer_id: tickets = [t for t in tickets if t.consumer_id == consumer_id]
        return tickets

    def by_priority(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), t in self._tickets.items():
            if inst == installation_id and t.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                counts[t.priority.value] = counts.get(t.priority.value, 0) + 1
        return counts

    def avg_resolution_hours(self, installation_id: str) -> float:
        resolved = [t for (inst, _), t in self._tickets.items() if inst == installation_id and t.resolved_at > 0]
        if not resolved: return 0.0
        total_h = sum((t.resolved_at - t.created_at) / 3600 for t in resolved)
        return round(total_h / len(resolved), 1)

    def _get(self, installation_id: str, ticket_id: str) -> SupportTicket:
        t = self._tickets.get((installation_id, ticket_id))
        if t is None: raise KeyError(f"Ticket {ticket_id} not found")
        return t
