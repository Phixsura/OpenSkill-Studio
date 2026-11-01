"""Fleet AI Streaming — track real-time LLM streaming."""
from __future__ import annotations
def fleet_ai_streaming(endpoints: list[dict]) -> dict:
    active = [e for e in endpoints if e.get("active", True)]
    active_streams = sum(e.get("active_streams", 0) for e in endpoints)
    tokens_streamed = sum(e.get("tokens_streamed_24h", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "active": len(active), "active_streams": active_streams,
            "tokens_streamed_24h": tokens_streamed, "all_active": len(active) == len(endpoints)}
