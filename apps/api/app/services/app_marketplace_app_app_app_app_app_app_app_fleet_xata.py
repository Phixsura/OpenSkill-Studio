"""Fleet Xata — track serverless database platform."""
from __future__ import annotations
def fleet_xata_status(databases: list[dict]) -> dict:
    active = [d for d in databases if d.get("active", True)]
    branches = sum(d.get("branches", 0) for d in databases)
    records = sum(d.get("records", 0) for d in databases)
    return {"databases": len(databases), "active": len(active), "branches": branches,
            "records": records, "all_active": len(active) == len(databases)}
