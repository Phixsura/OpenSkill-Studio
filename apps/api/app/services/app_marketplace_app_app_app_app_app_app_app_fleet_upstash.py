"""Fleet Upstash — track serverless Redis/Kafka health."""
from __future__ import annotations
def fleet_upstash_status(databases: list[dict]) -> dict:
    active = [d for d in databases if d.get("active", True)]
    total_commands = sum(d.get("commands_24h", 0) for d in databases)
    bandwidth_gb = sum(d.get("bandwidth_gb", 0) for d in databases)
    return {"databases": len(databases), "active": len(active), "commands_24h": total_commands,
            "bandwidth_gb": round(bandwidth_gb, 1), "healthy": len(active) == len(databases)}
