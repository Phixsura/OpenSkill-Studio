"""Fleet AI Data Loader v2 — track high-performance data loading."""
from __future__ import annotations
def fleet_ai_data_loader_v2(loaders: list[dict]) -> dict:
    active = [l for l in loaders if l.get("active", True)]
    throughput_gbps = round(sum(l.get("throughput_gbps", 0) for l in loaders), 1)
    prefetch_depth = max((l.get("prefetch", 0) for l in loaders), default=0)
    workers = sum(l.get("workers", 0) for l in loaders)
    return {"loaders": len(loaders), "active": len(active), "throughput_gbps": throughput_gbps,
            "prefetch": prefetch_depth, "workers": workers, "fast": throughput_gbps > 10}
