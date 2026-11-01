"""Fleet VictoriaMetrics — track VM cluster health."""
from __future__ import annotations
def fleet_vm_status(nodes: list[dict]) -> dict:
    healthy = [n for n in nodes if n.get("healthy", True)]
    rows_inserted = sum(n.get("rows_inserted_per_sec", 0) for n in nodes)
    storage_gb = sum(n.get("storage_gb", 0) for n in nodes)
    return {"nodes": len(nodes), "healthy": len(healthy), "rows_per_sec": rows_inserted,
            "storage_gb": storage_gb, "all_healthy": len(healthy) == len(nodes)}
