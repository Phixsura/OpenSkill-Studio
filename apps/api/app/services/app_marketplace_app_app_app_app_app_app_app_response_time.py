"""Response time tracker — SLA-aware response time monitoring."""
from __future__ import annotations
import math


def track_response_times(samples: list[float], *, sla_ms: float = 200) -> dict:
    if not samples:
        return {"count": 0, "error": "No samples"}
    s = sorted(samples)
    n = len(s)
    avg = round(sum(s) / n, 1)
    p50 = round(s[n // 2], 1)
    p95 = round(s[int(n * 0.95)], 1) if n > 1 else s[0]
    p99 = round(s[int(n * 0.99)], 1) if n > 1 else s[0]
    within_sla = sum(1 for v in s if v <= sla_ms)
    sla_pct = round(within_sla / n * 100, 1)
    return {
        "count": n, "min": round(s[0], 1), "max": round(s[-1], 1),
        "avg": avg, "p50": p50, "p95": p95, "p99": p99,
        "sla_ms": sla_ms, "within_sla": within_sla, "sla_pct": sla_pct,
        "sla_met": sla_pct >= 99.0,
        "status": "fast" if avg < sla_ms * 0.5 else "ok" if avg < sla_ms else "slow",
    }
