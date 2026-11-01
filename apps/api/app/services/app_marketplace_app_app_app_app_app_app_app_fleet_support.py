"""Fleet support tickets — track support load and resolution."""
from __future__ import annotations
def fleet_support_tickets(tickets: list[dict]) -> dict:
    open_tickets = [t for t in tickets if t.get("status") == "open"]
    resolved = [t for t in tickets if t.get("status") == "resolved"]
    avg_resolution = round(sum(t.get("resolution_hours", 0) for t in resolved) / max(len(resolved), 1), 1)
    return {"total": len(tickets), "open": len(open_tickets), "resolved": len(resolved),
            "avg_resolution_hours": avg_resolution, "backlog_healthy": len(open_tickets) < 50}
