"""Support Tickets — developer support system for marketplace extensions.

Manages support tickets between extension users and developers with
priority, categories, assignment, and resolution tracking.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_ON_USER = "waiting_on_user"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class TicketMessage:
    author_id: str
    body: str
    timestamp: str = ""
    is_internal: bool = False

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SupportTicket:
    ticket_id: str
    extension_id: str
    reporter_id: str
    subject: str
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    category: str = "general"
    assigned_to: str = ""
    messages: list[TicketMessage] = field(default_factory=list)
    created_at: str = ""
    resolved_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class SupportTicketService:
    """Manages extension support tickets."""

    def __init__(self):
        self._tickets: dict[str, SupportTicket] = {}

    def create_ticket(self, ticket_id: str, extension_id: str, reporter_id: str,
                      subject: str, body: str, priority: TicketPriority = TicketPriority.MEDIUM,
                      category: str = "general") -> SupportTicket:
        ticket = SupportTicket(
            ticket_id=ticket_id, extension_id=extension_id,
            reporter_id=reporter_id, subject=subject,
            priority=priority, category=category,
            messages=[TicketMessage(author_id=reporter_id, body=body)],
        )
        self._tickets[ticket_id] = ticket
        return ticket

    def reply(self, ticket_id: str, author_id: str, body: str,
              is_internal: bool = False) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket or ticket.status == TicketStatus.CLOSED:
            return False
        ticket.messages.append(TicketMessage(author_id, body, is_internal=is_internal))
        if ticket.status == TicketStatus.WAITING_ON_USER and author_id == ticket.reporter_id:
            ticket.status = TicketStatus.IN_PROGRESS
        return True

    def assign(self, ticket_id: str, assignee_id: str) -> bool:
        ticket = self._tickets.get(ticket_id)
        if ticket:
            ticket.assigned_to = assignee_id
            if ticket.status == TicketStatus.OPEN:
                ticket.status = TicketStatus.IN_PROGRESS
            return True
        return False

    def resolve(self, ticket_id: str) -> bool:
        ticket = self._tickets.get(ticket_id)
        if ticket and ticket.status not in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            ticket.status = TicketStatus.RESOLVED
            ticket.resolved_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def close(self, ticket_id: str) -> bool:
        ticket = self._tickets.get(ticket_id)
        if ticket:
            ticket.status = TicketStatus.CLOSED
            return True
        return False

    def list_tickets(self, extension_id: str | None = None,
                     status: TicketStatus | None = None,
                     assigned_to: str | None = None) -> list[SupportTicket]:
        tickets = list(self._tickets.values())
        if extension_id:
            tickets = [t for t in tickets if t.extension_id == extension_id]
        if status:
            tickets = [t for t in tickets if t.status == status]
        if assigned_to:
            tickets = [t for t in tickets if t.assigned_to == assigned_to]
        return sorted(tickets, key=lambda t: t.created_at, reverse=True)

    def get_stats(self, extension_id: str) -> dict:
        tickets = [t for t in self._tickets.values() if t.extension_id == extension_id]
        by_status = {s.value: 0 for s in TicketStatus}
        for t in tickets:
            by_status[t.status.value] += 1
        return {
            "extension_id": extension_id, "total": len(tickets),
            "by_status": by_status, "open": by_status["open"] + by_status["in_progress"],
        }
