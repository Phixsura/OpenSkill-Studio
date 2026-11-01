"""Consumer API Support Ticket — manage support tickets from API consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class SupportTicket:
    ticket_id: str
    consumer_id: str
    subject: str
    description: str
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    status: str = "open"  # "open", "in_progress", "waiting", "resolved", "closed"
    created_at: datetime | None = None
    resolved_at: datetime | None = None
    assigned_to: str = ""

@dataclass
class TicketReply:
    reply_id: str
    ticket_id: str
    author: str
    message: str
    is_staff: bool = False
    created_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket:
    def __init__(self) -> None:
        self._tickets: dict[tuple[str, str], SupportTicket] = {}
        self._replies: dict[tuple[str, str], list[TicketReply]] = {}

    def create(self, installation_id: str, ticket: SupportTicket) -> SupportTicket:
        if not installation_id:
            raise ValueError("installation_id is required")
        if ticket.priority not in ("low", "normal", "high", "urgent"):
            raise ValueError(f"Invalid priority: {ticket.priority}")
        if not ticket.subject:
            raise ValueError("subject is required")
        ticket.created_at = ticket.created_at or datetime.utcnow()
        ticket.status = "open"
        self._tickets[(installation_id, ticket.ticket_id)] = ticket
        return ticket

    def update_status(self, installation_id: str, ticket_id: str, status: str, now: datetime | None = None) -> SupportTicket:
        key = (installation_id, ticket_id)
        ticket = self._tickets.get(key)
        if not ticket:
            raise ValueError("Ticket not found")
        if status not in ("open", "in_progress", "waiting", "resolved", "closed"):
            raise ValueError(f"Invalid status: {status}")
        ticket.status = status
        if status in ("resolved", "closed"):
            ticket.resolved_at = now or datetime.utcnow()
        return ticket

    def add_reply(self, installation_id: str, reply: TicketReply) -> TicketReply:
        key = (installation_id, reply.ticket_id)
        if key not in self._tickets:
            raise ValueError("Ticket not found")
        reply.created_at = reply.created_at or datetime.utcnow()
        if key not in self._replies:
            self._replies[key] = []
        self._replies[key].append(reply)
        return reply

    def get_replies(self, installation_id: str, ticket_id: str) -> list[TicketReply]:
        return self._replies.get((installation_id, ticket_id), [])

    def list_tickets(self, installation_id: str, consumer_id: str | None = None, status: str | None = None) -> list[SupportTicket]:
        tickets = [t for (inst, _), t in self._tickets.items() if inst == installation_id]
        if consumer_id:
            tickets = [t for t in tickets if t.consumer_id == consumer_id]
        if status:
            tickets = [t for t in tickets if t.status == status]
        return sorted(tickets, key=lambda t: {"urgent": 0, "high": 1, "normal": 2, "low": 3}.get(t.priority, 4))
