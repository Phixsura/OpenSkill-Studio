"""Fleet AI Function Calling — track tool-use in LLM agents."""
from __future__ import annotations
def fleet_ai_func_calling(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    calls_24h = sum(s.get("function_calls_24h", 0) for s in services)
    tools_registered = sum(s.get("tools", 0) for s in services)
    success_rate = round(sum(s.get("success_rate", 100) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "calls_24h": calls_24h,
            "tools": tools_registered, "success_rate": success_rate}
