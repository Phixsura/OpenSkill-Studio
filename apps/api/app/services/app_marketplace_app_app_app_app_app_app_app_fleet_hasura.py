"""Fleet Hasura — track instant GraphQL engine health."""
from __future__ import annotations
def fleet_hasura_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    tables = sum(i.get("tables", 0) for i in instances)
    requests_24h = sum(i.get("requests_24h", 0) for i in instances)
    return {"instances": len(instances), "healthy": len(healthy), "tables": tables,
            "requests_24h": requests_24h, "all_healthy": len(healthy) == len(instances)}
