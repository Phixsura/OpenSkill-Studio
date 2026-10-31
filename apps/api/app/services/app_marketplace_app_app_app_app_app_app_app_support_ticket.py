"""Support ticket system — create, track, and resolve support tickets."""
from __future__ import annotations
import secrets
import html


class SupportTicketSystem:
    def __init__(self):
        self._tickets: list[dict] = []

    def create(self, *, title: str, description: str, priority: str = "medium",
                category: str = "general", user_id: str = "") -> dict:
        tid = f"TKT-{len(self._tickets) + 1:04d}"
        self._tickets.append({
            "id": tid, "title": html.escape(title),
            "description": html.escape(description[:2000]),
            "priority": priority, "category": category,
            "user_id": user_id, "status": "open", "replies": [],
        })
        return {"id": tid, "status": "open", "priority": priority}

    def reply(self, ticket_id: str, *, message: str, author: str) -> dict:
        t = next((t for t in self._tickets if t["id"] == ticket_id), None)
        if not t:
            return {"error": "Ticket not found"}
        t["replies"].append({"message": html.escape(message[:1000]), "author": author})
        return {"replied": True, "reply_count": len(t["replies"])}

    def resolve(self, ticket_id: str) -> dict:
        t = next((t for t in self._tickets if t["id"] == ticket_id), None)
        if not t:
            return {"error": "Ticket not found"}
        t["status"] = "resolved"
        return {"resolved": True, "id": ticket_id}

    def list_tickets(self, *, status: str | None = None) -> list[dict]:
        tickets = self._tickets
        if status:
            tickets = [t for t in tickets if t["status"] == status]
        return [{"id": t["id"], "title": t["title"], "priority": t["priority"],
                 "status": t["status"], "replies": len(t["replies"])}
                for t in reversed(tickets)]

    def stats(self) -> dict:
        open_count = sum(1 for t in self._tickets if t["status"] == "open")
        return {"total": len(self._tickets), "open": open_count,
                "resolved": len(self._tickets) - open_count}
