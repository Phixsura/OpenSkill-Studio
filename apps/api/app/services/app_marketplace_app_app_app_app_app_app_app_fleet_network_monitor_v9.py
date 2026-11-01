"""Fleet Network Monitor v9 — track network interface health and throughput."""
from __future__ import annotations
def fleet_network_monitor_v9(interfaces: list[dict]) -> dict:
    up = [i for i in interfaces if i.get("status") == "up"]
    rx_gbps = sum(i.get("rx_gbps", 0) for i in interfaces)
    tx_gbps = sum(i.get("tx_gbps", 0) for i in interfaces)
    errors = sum(i.get("errors", 0) for i in interfaces)
    return {"interfaces": len(interfaces), "up": len(up), "rx_gbps": round(rx_gbps, 1),
            "tx_gbps": round(tx_gbps, 1), "errors": errors, "healthy": errors == 0}
