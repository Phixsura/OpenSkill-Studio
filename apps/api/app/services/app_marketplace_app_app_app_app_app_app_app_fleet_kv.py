"""Fleet KV Store — track edge key-value storage."""
from __future__ import annotations
def fleet_kv_store(namespaces: list[dict]) -> dict:
    keys = sum(n.get("keys", 0) for n in namespaces)
    reads_24h = sum(n.get("reads_24h", 0) for n in namespaces)
    writes_24h = sum(n.get("writes_24h", 0) for n in namespaces)
    return {"namespaces": len(namespaces), "keys": keys, "reads_24h": reads_24h,
            "writes_24h": writes_24h, "active": reads_24h > 0}
