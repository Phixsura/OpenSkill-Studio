"""Fleet Cosmos DB — track globally distributed NoSQL health."""
from __future__ import annotations
def fleet_cosmosdb_status(accounts: list[dict]) -> dict:
    available = [a for a in accounts if a.get("status") == "Online"]
    total_ru = sum(a.get("consumed_ru_per_sec", 0) for a in accounts)
    regions = len(set(r for a in accounts for r in a.get("regions", [])))
    return {"accounts": len(accounts), "available": len(available), "consumed_ru_per_sec": total_ru,
            "regions": regions, "globally_distributed": regions >= 3}
