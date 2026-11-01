"""API latency percentile tracker — compute p50, p90, p95, p99 from samples."""
from __future__ import annotations
import math


def compute_percentiles(samples: list[float]) -> dict:
    if not samples:
        return {"count": 0, "percentiles": {}, "error": "No samples"}
    s = sorted(samples)
    n = len(s)
    def pct(p: float) -> float:
        idx = (p / 100) * (n - 1)
        lo = int(math.floor(idx))
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        return round(s[lo] + frac * (s[hi] - s[lo]), 2)
    p = {50: pct(50), 90: pct(90), 95: pct(95), 99: pct(99)}
    avg = round(sum(s) / n, 2)
    return {
        "count": n, "min": s[0], "max": s[-1], "avg": avg,
        "percentiles": p,
        "p50": p[50], "p90": p[90], "p95": p[95], "p99": p[99],
        "status": "fast" if p[95] < 200 else "ok" if p[95] < 500 else "slow",
    }


def compare_latency(current: dict, previous: dict) -> dict:
    if not current.get("percentiles") or not previous.get("percentiles"):
        return {"comparable": False}
    changes = {}
    for pct in (50, 90, 95, 99):
        cur = current["percentiles"].get(pct, 0)
        prev = previous["percentiles"].get(pct, 0)
        delta = round(cur - prev, 2)
        changes[f"p{pct}"] = {"current": cur, "previous": prev, "delta": delta,
                               "direction": "faster" if delta < 0 else "slower" if delta > 0 else "same"}
    return {"comparable": True, "changes": changes}
