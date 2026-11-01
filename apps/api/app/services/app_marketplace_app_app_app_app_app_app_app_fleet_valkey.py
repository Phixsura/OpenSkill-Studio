"""Fleet Valkey — track open-source Redis fork."""
from __future__ import annotations
def fleet_valkey_status(nodes: list[dict]) -> dict:
    online = [n for n in nodes if n.get("online", True)]
    total_keys = sum(n.get("keys", 0) for n in nodes)
    memory_gb = sum(n.get("memory_gb", 0) for n in nodes)
    return {"nodes": len(nodes), "online": len(online), "keys": total_keys,
            "memory_gb": round(memory_gb, 1), "all_online": len(online) == len(nodes)}
