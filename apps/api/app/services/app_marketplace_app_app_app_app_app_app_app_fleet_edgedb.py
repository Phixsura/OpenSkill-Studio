"""Fleet EdgeDB — track graph-relational database."""
from __future__ import annotations
def fleet_edgedb_status(instances: list[dict]) -> dict:
    available = [i for i in instances if i.get("available", True)]
    branches = sum(i.get("branches", 0) for i in instances)
    types = sum(i.get("types", 0) for i in instances)
    return {"instances": len(instances), "available": len(available), "branches": branches,
            "types": types, "all_available": len(available) == len(instances)}
