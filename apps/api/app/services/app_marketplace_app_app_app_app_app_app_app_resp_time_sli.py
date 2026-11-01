"""Response time SLI — track response time service level indicators."""
from __future__ import annotations


def calculate_sli(latencies: list[float], threshold_ms: float = 200) -> dict:
    if not latencies:
        return {"sli_pct": 100, "samples": 0}
    good = sum(1 for l in latencies if l <= threshold_ms)
    sli = round(good / len(latencies) * 100, 3)
    s = sorted(latencies)
    n = len(s)
    return {"sli_pct": sli, "samples": n, "threshold_ms": threshold_ms,
            "good_count": good, "bad_count": n - good,
            "p50": s[n // 2], "p99": s[int(n * 0.99)]}


def sli_trend(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "insufficient_data"}
    recent = snapshots[-1]["sli_pct"]
    prev = snapshots[-2]["sli_pct"]
    trend = "improving" if recent > prev + 0.1 else ("degrading" if recent < prev - 0.1 else "stable")
    return {"trend": trend, "current": recent, "previous": prev,
            "delta": round(recent - prev, 3)}
