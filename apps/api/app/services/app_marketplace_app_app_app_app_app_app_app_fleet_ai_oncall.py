"""Fleet AI On-Call Scheduler — track AI ops on-call rotation management."""
from __future__ import annotations
def fleet_ai_oncall(schedulers: list[dict]) -> dict:
    active = [s for s in schedulers if s.get("active", True)]
    engineers = sum(s.get("engineers", 0) for s in schedulers)
    pages_24h = sum(s.get("pages_24h", 0) for s in schedulers)
    ack_time_min = round(sum(s.get("ack_min", 0) for s in schedulers) / max(len(schedulers), 1), 1)
    return {"schedulers": len(schedulers), "active": len(active), "engineers": engineers,
            "pages_24h": pages_24h, "ack_min": ack_time_min, "responsive": ack_time_min < 5}
