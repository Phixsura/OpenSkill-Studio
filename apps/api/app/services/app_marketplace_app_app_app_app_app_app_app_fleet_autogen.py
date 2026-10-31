"""Fleet AutoGen — track multi-agent conversation framework."""
from __future__ import annotations
def fleet_autogen_status(groups: list[dict]) -> dict:
    active = [g for g in groups if g.get("active", True)]
    conversations = sum(g.get("conversations_24h", 0) for g in groups)
    agents = sum(g.get("agents", 0) for g in groups)
    return {"groups": len(groups), "active": len(active), "conversations_24h": conversations,
            "agents": agents, "all_active": len(active) == len(groups)}
