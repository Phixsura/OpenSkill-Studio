"""Fleet AI On-Call v7 — track AI-powered on-call management."""
from __future__ import annotations
def fleet_ai_oncall_v7(schedulers: list[dict]) -> dict:
    active = [s for s in schedulers if s.get("active", True)]
    engineers = sum(s.get("engineers", 0) for s in schedulers)
    pages_24h = sum(s.get("pages", 0) for s in schedulers)
    ack_time = round(sum(s.get("ack_min", 0) for s in schedulers) / max(len(schedulers), 1), 1)
    auto_mitigated = sum(s.get("auto", 0) for s in schedulers)
    return {"schedulers": len(schedulers), "active": len(active), "engineers": engineers,
            "pages": pages_24h, "ack_min": ack_time, "auto": auto_mitigated, "responsive": ack_time < 3}
