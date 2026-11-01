"""Fleet Bedrock — track AWS foundation model service."""
from __future__ import annotations
def fleet_bedrock_status(models: list[dict]) -> dict:
    available = [m for m in models if m.get("available", True)]
    invocations_24h = sum(m.get("invocations_24h", 0) for m in models)
    tokens_24h = sum(m.get("tokens_24h", 0) for m in models)
    return {"models": len(models), "available": len(available), "invocations_24h": invocations_24h,
            "tokens_24h": tokens_24h, "all_available": len(available) == len(models)}
