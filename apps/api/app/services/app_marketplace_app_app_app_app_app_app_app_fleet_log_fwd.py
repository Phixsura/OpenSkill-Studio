"""Fleet log forwarding — track log pipeline delivery."""
from __future__ import annotations
def fleet_log_forwarding(agents: list[dict]) -> dict:
    healthy = [a for a in agents if a.get("status") == "running"]
    buffered = sum(a.get("buffer_mb", 0) for a in agents)
    dropped = sum(a.get("dropped_events", 0) for a in agents)
    return {"agents": len(agents), "healthy": len(healthy), "buffer_mb": buffered,
            "dropped": dropped, "reliable": dropped == 0}
