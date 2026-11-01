"""Fleet Vercel AI SDK — track AI-powered web apps."""
from __future__ import annotations
def fleet_vercel_ai_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    streams_24h = sum(a.get("streams_24h", 0) for a in apps)
    tokens_24h = sum(a.get("tokens_24h", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "streams_24h": streams_24h,
            "tokens_24h": tokens_24h, "all_deployed": len(deployed) == len(apps)}
