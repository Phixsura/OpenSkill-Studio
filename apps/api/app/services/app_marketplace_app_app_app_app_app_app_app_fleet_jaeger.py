"""Fleet Jaeger — track distributed tracing storage."""
from __future__ import annotations
def fleet_jaeger_status(collectors: list[dict]) -> dict:
    healthy = [c for c in collectors if c.get("healthy", True)]
    spans_per_sec = sum(c.get("spans_per_sec", 0) for c in collectors)
    storage_gb = sum(c.get("storage_gb", 0) for c in collectors)
    return {"collectors": len(collectors), "healthy": len(healthy), "spans_per_sec": spans_per_sec,
            "storage_gb": storage_gb, "all_healthy": len(healthy) == len(collectors)}
