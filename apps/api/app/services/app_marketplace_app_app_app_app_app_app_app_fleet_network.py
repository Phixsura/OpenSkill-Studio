"""Fleet network throughput — aggregate network I/O across the fleet."""
from __future__ import annotations
def fleet_network_throughput(services: list[dict]) -> dict:
    rx = sum(s.get("rx_mbps", 0) for s in services)
    tx = sum(s.get("tx_mbps", 0) for s in services)
    return {"rx_mbps": round(rx, 1), "tx_mbps": round(tx, 1),
            "total_mbps": round(rx + tx, 1), "services": len(services)}
