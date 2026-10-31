"""Fleet AI Data Versioning — track dataset version control."""
from __future__ import annotations
def fleet_ai_data_versioning(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    datasets = sum(s.get("datasets", 0) for s in systems)
    versions = sum(s.get("versions", 0) for s in systems)
    storage_tb = round(sum(s.get("storage_tb", 0) for s in systems), 1)
    return {"systems": len(systems), "active": len(active), "datasets": datasets,
            "versions": versions, "storage_tb": storage_tb, "versioned": versions > datasets}
