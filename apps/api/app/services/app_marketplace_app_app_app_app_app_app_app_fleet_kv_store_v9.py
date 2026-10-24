"""Fleet KV Store v9 — track key-value store operations and latency."""
from __future__ import annotations
def fleet_kv_store_v9(clusters: list[dict]) -> dict:
    ops_sec = sum(c.get("ops_per_sec", 0) for c in clusters)
    avg_latency = sum(c.get("latency_us", 0) for c in clusters) / len(clusters) if clusters else 0
    keys = sum(c.get("total_keys", 0) for c in clusters)
    return {"clusters": len(clusters), "ops_per_sec": ops_sec, "avg_latency_us": round(avg_latency, 1),
            "total_keys": keys, "healthy": avg_latency < 1000}
