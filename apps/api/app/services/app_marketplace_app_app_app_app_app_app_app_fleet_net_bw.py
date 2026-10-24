"""Fleet network bandwidth — track bandwidth utilization."""
from __future__ import annotations
def fleet_net_bandwidth(interfaces: list[dict]) -> dict:
    total_bw = sum(i.get("capacity_gbps", 0) for i in interfaces)
    used_bw = sum(i.get("used_gbps", 0) for i in interfaces)
    pct = round(used_bw / max(total_bw, 0.01) * 100, 1)
    return {"total_gbps": total_bw, "used_gbps": round(used_bw, 1), "util_pct": pct, "saturated": pct > 80}
