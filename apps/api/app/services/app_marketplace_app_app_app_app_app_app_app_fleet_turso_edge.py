"""Fleet Turso edge — track edge SQLite replication."""
from __future__ import annotations
def fleet_turso_edge_status(groups: list[dict]) -> dict:
    primary = sum(g.get("primary", 0) for g in groups)
    replicas = sum(g.get("replicas", 0) for g in groups)
    locations = sum(g.get("locations", 0) for g in groups)
    return {"groups": len(groups), "primary": primary, "replicas": replicas,
            "locations": locations, "distributed": locations >= 3}
