"""Fleet Mimir — track long-term metrics storage."""
from __future__ import annotations
def fleet_mimir_status(clusters: list[dict]) -> dict:
    healthy = [c for c in clusters if c.get("healthy", True)]
    total_series = sum(c.get("active_series", 0) for c in clusters)
    ingestion_rate = sum(c.get("samples_per_sec", 0) for c in clusters)
    return {"clusters": len(clusters), "healthy": len(healthy), "total_series": total_series,
            "samples_per_sec": ingestion_rate, "all_healthy": len(healthy) == len(clusters)}
