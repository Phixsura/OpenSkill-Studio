"""Fleet Node Drain v9 — track K8s node cordoning and draining."""
from __future__ import annotations
def fleet_node_drain_v9(nodes: list[dict]) -> dict:
    cordoned = [n for n in nodes if n.get("cordoned")]
    draining = [n for n in nodes if n.get("draining")]
    drained = [n for n in nodes if n.get("drained")]
    return {"nodes": len(nodes), "cordoned": len(cordoned), "draining": len(draining),
            "drained": len(drained), "healthy": len(draining) == 0}
