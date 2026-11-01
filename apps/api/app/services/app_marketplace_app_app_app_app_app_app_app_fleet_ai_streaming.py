"""Fleet AI Streaming — track real-time AI response streaming."""
from __future__ import annotations
def fleet_ai_streaming(streams: list[dict]) -> dict:
    active = [s for s in streams if s.get("active", True)]
    connections = sum(s.get("connections", 0) for s in streams)
    tokens_per_sec = sum(s.get("tokens_per_sec", 0) for s in streams)
    ttft_ms = min((s.get("ttft_ms", 9999) for s in streams), default=9999)
    return {"streams": len(streams), "active": len(active), "connections": connections,
            "tokens_per_sec": tokens_per_sec, "ttft_ms": ttft_ms, "responsive": ttft_ms < 500}
