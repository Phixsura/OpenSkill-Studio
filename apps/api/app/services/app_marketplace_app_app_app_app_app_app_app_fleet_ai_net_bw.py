"""Fleet AI Network Bandwidth — track AI service network throughput."""
from __future__ import annotations
def fleet_ai_network_bandwidth(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    ingress_gbps = round(sum(m.get("ingress_gbps", 0) for m in monitors), 1)
    egress_gbps = round(sum(m.get("egress_gbps", 0) for m in monitors), 1)
    utilization = round(sum(m.get("util_pct", 0) for m in monitors) / max(len(monitors), 1), 1)
    return {"monitors": len(monitors), "active": len(active), "ingress_gbps": ingress_gbps,
            "egress_gbps": egress_gbps, "utilization": utilization, "healthy": utilization < 80}
