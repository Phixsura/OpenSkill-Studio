"""Fleet Service Mesh Perf v9 — track mesh proxy overhead and latency."""
from __future__ import annotations
def fleet_service_mesh_perf_v9(proxies: list[dict]) -> dict:
    avg_overhead = sum(p.get("overhead_ms", 0) for p in proxies) / len(proxies) if proxies else 0
    cpu_overhead = sum(p.get("cpu_overhead_pct", 0) for p in proxies) / len(proxies) if proxies else 0
    mem_overhead = sum(p.get("mem_overhead_mb", 0) for p in proxies)
    return {"proxies": len(proxies), "avg_overhead_ms": round(avg_overhead, 2),
            "avg_cpu_overhead_pct": round(cpu_overhead, 1), "total_mem_mb": round(mem_overhead, 1),
            "healthy": avg_overhead < 5}
