"""Fleet Cortex — track horizontally scalable metrics backend."""
from __future__ import annotations
def fleet_cortex_status(clusters: list[dict]) -> dict:
    healthy = [c for c in clusters if c.get("healthy", True)]
    series = sum(c.get("active_series", 0) for c in clusters)
    ingestion = sum(c.get("samples_per_sec", 0) for c in clusters)
    return {"clusters": len(clusters), "healthy": len(healthy), "active_series": series,
            "ingestion_rate": ingestion, "all_healthy": len(healthy) == len(clusters)}
