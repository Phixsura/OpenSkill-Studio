"""Fleet API Request Log v9 — track structured API request logging."""
from __future__ import annotations
def fleet_api_request_log_v9(loggers: list[dict]) -> dict:
    enabled = [l for l in loggers if l.get("enabled")]
    entries_sec = sum(l.get("entries_per_sec", 0) for l in loggers)
    storage_gb = sum(l.get("storage_gb", 0) for l in loggers)
    return {"loggers": len(loggers), "enabled": len(enabled), "entries_per_sec": entries_sec,
            "storage_gb": round(storage_gb, 1), "healthy": len(enabled) == len(loggers)}
