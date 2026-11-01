"""Fleet AI Logging v4 — track centralized structured logging at scale."""
from __future__ import annotations
def fleet_ai_logging_v4(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    logs_24h = sum(s.get("logs_24h", 0) for s in systems)
    storage_tb = round(sum(s.get("storage_tb", 0) for s in systems), 1)
    retention_days = max((s.get("retention_days", 0) for s in systems), default=0)
    searchable = all(s.get("indexed", False) for s in systems)
    return {"systems": len(systems), "active": len(active), "logs_24h": logs_24h,
            "storage_tb": storage_tb, "retention_days": retention_days, "searchable": searchable}
