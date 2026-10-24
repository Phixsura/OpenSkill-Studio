"""Fleet Network Perf v9 — track network latency and packet loss."""
from __future__ import annotations
def fleet_network_perf_v9(links: list[dict]) -> dict:
    healthy_links = [l for l in links if l.get("packet_loss", 0) < 0.1]
    avg_latency = sum(l.get("latency_ms", 0) for l in links) / len(links) if links else 0
    bandwidth = sum(l.get("bandwidth_gbps", 0) for l in links)
    return {"links": len(links), "healthy": len(healthy_links), "avg_latency_ms": round(avg_latency, 1),
            "total_bandwidth_gbps": round(bandwidth, 1), "healthy": len(healthy_links) == len(links)}
