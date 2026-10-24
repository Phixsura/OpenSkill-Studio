"""Fleet K9s — track K9s terminal dashboard usage."""
from __future__ import annotations
def fleet_k9s_usage(users: list[dict]) -> dict:
    active = [u for u in users if u.get("active_24h", False)]
    total_commands = sum(u.get("commands_24h", 0) for u in active)
    return {"total_users": len(users), "active_24h": len(active),
            "commands_24h": total_commands, "popular": len(active) > 10}
