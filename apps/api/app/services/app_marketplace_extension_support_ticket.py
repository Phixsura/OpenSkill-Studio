"""Extension Support Ticket — support tickets between users and developers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class TicketMessage:
    sender_id: str
    content: str
    sent_at: float = 0.0
    def __post_init__(self):
        if not self.sent_at: self.sent_at = time.time()


@dataclass
class SupportTicket:
    ticket_id: str
    extension_id: str
    user_id: str
    subject: str
    priority: str = "normal"  # low, normal, high, urgent
    status: str = "open"  # open, in_progress, waiting, resolved, closed
    messages: list[TicketMessage] = field(default_factory=list)
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtSupportTicketService:
    def __init__(self):
        self._tickets: dict[str, SupportTicket] = {}
        self._counter = 0

    def create(self, extension_id: str, user_id: str, subject: str,
               message: str, priority: str = "normal") -> SupportTicket:
        self._counter += 1
        tid = f"tkt-{self._counter}"
        ticket = SupportTicket(ticket_id=tid, extension_id=extension_id,
                               user_id=user_id, subject=subject, priority=priority)
        ticket.messages.append(TicketMessage(sender_id=user_id, content=message))
        self._tickets[tid] = ticket
        return ticket

    def reply(self, ticket_id: str, sender_id: str, content: str) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket or ticket.status == "closed":
            return False
        ticket.messages.append(TicketMessage(sender_id=sender_id, content=content))
        if ticket.status == "open":
            ticket.status = "in_progress"
        return True

    def update_status(self, ticket_id: str, status: str) -> bool:
        ticket = self._tickets.get(ticket_id)
        if not ticket or status not in ("open", "in_progress", "waiting", "resolved", "closed"):
            return False
        ticket.status = status
        return True

    def get_by_extension(self, extension_id: str, status: str | None = None) -> list[SupportTicket]:
        tickets = [t for t in self._tickets.values() if t.extension_id == extension_id]
        if status:
            tickets = [t for t in tickets if t.status == status]
        return sorted(tickets, key=lambda t: {"urgent": 0, "high": 1, "normal": 2, "low": 3}.get(t.priority, 2))

    def get_by_user(self, user_id: str) -> list[SupportTicket]:
        return [t for t in self._tickets.values() if t.user_id == user_id]
