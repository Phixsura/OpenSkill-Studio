"""Fleet AI Response Streamer — track SSE/WebSocket AI response streaming."""
from __future__ import annotations
def fleet_ai_response_streamer(streamers: list[dict]) -> dict:
    active = [s for s in streamers if s.get("active", True)]
    streams_24h = sum(s.get("streams_24h", 0) for s in streamers)
    tokens_streamed = sum(s.get("tokens", 0) for s in streamers)
    avg_ttft_ms = round(sum(s.get("ttft_ms", 0) for s in streamers) / max(len(streamers), 1), 1)
    return {"streamers": len(streamers), "active": len(active), "streams_24h": streams_24h,
            "tokens": tokens_streamed, "ttft_ms": avg_ttft_ms, "responsive": avg_ttft_ms < 200}
