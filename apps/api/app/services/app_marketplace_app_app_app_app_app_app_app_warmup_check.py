"""Warm-up health check — verify services are ready after startup."""
from __future__ import annotations
import time


def run_warmup(services: list[dict]) -> dict:
    results = []
    all_ready = True
    for s in services:
        ready = s.get("health") == "ok" and s.get("latency_ms", 9999) < s.get("threshold_ms", 1000)
        if not ready:
            all_ready = False
        results.append({"name": s["name"], "ready": ready,
                         "latency_ms": s.get("latency_ms", 0),
                         "threshold_ms": s.get("threshold_ms", 1000)})
    total = len(results)
    ready_count = sum(1 for r in results if r["ready"])
    return {"services": results, "total": total, "ready": ready_count,
            "not_ready": total - ready_count, "all_ready": all_ready,
            "warmup_complete": all_ready}


def estimate_warmup_time(services: list[dict]) -> dict:
    max_latency = max((s.get("warmup_sec", 5) for s in services), default=0)
    total = sum(s.get("warmup_sec", 5) for s in services)
    return {"max_warmup_sec": max_latency, "total_sequential_sec": total,
            "estimated_parallel_sec": max_latency,
            "service_count": len(services)}
