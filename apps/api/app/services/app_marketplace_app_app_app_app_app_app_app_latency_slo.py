"""Endpoint latency SLO checker — check if endpoints meet latency SLOs."""
from __future__ import annotations


def check_latency_slo(endpoints: list[dict]) -> dict:
    results = []
    for ep in endpoints:
        p99 = ep.get("p99_ms", 0)
        target = ep.get("target_p99_ms", 500)
        met = p99 <= target
        headroom = round(target - p99, 1)
        results.append({"endpoint": ep["endpoint"], "p99_ms": p99,
                        "target_ms": target, "met": met, "headroom_ms": max(0, headroom)})
    met_count = sum(1 for r in results if r["met"])
    return {"endpoints": results, "total": len(results), "met": met_count,
            "breached": len(results) - met_count,
            "compliance_pct": round(met_count / max(len(results), 1) * 100, 1)}
