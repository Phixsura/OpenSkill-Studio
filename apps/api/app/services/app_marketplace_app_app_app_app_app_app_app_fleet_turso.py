"""Fleet Turso — track edge SQLite database health."""
from __future__ import annotations
def fleet_turso_status(databases: list[dict]) -> dict:
    replicas = sum(d.get("replicas", 0) for d in databases)
    total_rows = sum(d.get("rows", 0) for d in databases)
    locations = len(set(loc for d in databases for loc in d.get("locations", [])))
    return {"databases": len(databases), "replicas": replicas, "total_rows": total_rows,
            "locations": locations, "globally_distributed": locations >= 3}
