"""Fleet KeyDB — track multi-threaded Redis fork."""
from __future__ import annotations
def fleet_keydb_status(nodes: list[dict]) -> dict:
    online = [n for n in nodes if n.get("online", True)]
    total_keys = sum(n.get("keys", 0) for n in nodes)
    ops_per_sec = sum(n.get("ops_per_sec", 0) for n in nodes)
    return {"nodes": len(nodes), "online": len(online), "keys": total_keys,
            "ops_per_sec": ops_per_sec, "all_online": len(online) == len(nodes)}
