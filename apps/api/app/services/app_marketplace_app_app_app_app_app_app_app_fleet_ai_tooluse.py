"""Fleet AI Tool Use — track AI agent tool invocations."""
from __future__ import annotations
def fleet_ai_tooluse(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    tool_calls_24h = sum(s.get("tool_calls_24h", 0) for s in services)
    tools_available = sum(s.get("tools", 0) for s in services)
    success_rate = round(sum(s.get("success_rate", 100) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "tool_calls_24h": tool_calls_24h,
            "tools": tools_available, "success_rate": success_rate}
