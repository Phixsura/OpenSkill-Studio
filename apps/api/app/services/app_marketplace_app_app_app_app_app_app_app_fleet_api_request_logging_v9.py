"""Fleet API Request Logging v9 — track structured request audit logging."""
from __future__ import annotations
def fleet_api_request_logging_v9(loggers: list[dict]) -> dict:
    structured = [l for l in loggers if l.get("structured")]
    entries = sum(l.get("entries_today", 0) for l in loggers)
    size_gb = sum(l.get("size_gb", 0) for l in loggers)
    return {"loggers": len(loggers), "structured": len(structured), "entries_today": entries,
            "size_gb_today": round(size_gb, 1), "healthy": len(structured) == len(loggers)}
