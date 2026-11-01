"""Fleet Network Latency v9 — track inter-service network latency."""
from __future__ import annotations
def fleet_network_latency_v9(paths: list[dict]) -> dict:
    within_sla = [p for p in paths if p.get("latency_ms", 0) < p.get("sla_ms", 100)]
    avg = sum(p.get("latency_ms", 0) for p in paths) / len(paths) if paths else 0
    p99 = max((p.get("p99_ms", 0) for p in paths), default=0)
    return {"paths": len(paths), "within_sla": len(within_sla), "avg_ms": round(avg, 1),
            "p99_ms": p99, "healthy": len(within_sla) == len(paths)}
