"""Fleet Consul — track Consul service mesh and KV store."""
from __future__ import annotations
def fleet_consul_status(datacenters: list[dict]) -> dict:
    healthy = [d for d in datacenters if d.get("healthy", True)]
    total_services = sum(d.get("services", 0) for d in datacenters)
    kv_keys = sum(d.get("kv_keys", 0) for d in datacenters)
    return {"datacenters": len(datacenters), "healthy": len(healthy), "services": total_services,
            "kv_keys": kv_keys, "all_healthy": len(healthy) == len(datacenters)}
