"""Fleet VPN Gateway v9 — track VPN tunnel health and throughput."""
from __future__ import annotations
def fleet_vpn_gateway_v9(tunnels: list[dict]) -> dict:
    up = [t for t in tunnels if t.get("status") == "up"]
    bandwidth = sum(t.get("bandwidth_mbps", 0) for t in tunnels)
    peers = len({t.get("peer") for t in tunnels if t.get("peer")})
    return {"tunnels": len(tunnels), "up": len(up), "bandwidth_mbps": bandwidth,
            "unique_peers": peers, "healthy": len(up) == len(tunnels)}
