"""API endpoint latency histogram — track latency distribution per endpoint."""
from __future__ import annotations


BUCKETS = [5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]


def build_histogram(latencies: list[float]) -> dict:
    counts = {f"le_{b}": 0 for b in BUCKETS}
    counts["le_inf"] = len(latencies)
    for l in latencies:
        for b in BUCKETS:
            if l <= b:
                counts[f"le_{b}"] += 1
    total = len(latencies)
    pcts = {}
    for k, v in counts.items():
        pcts[k] = round(v / max(total, 1) * 100, 1)
    return {"counts": counts, "percentages": pcts, "total": total}


def compare_histograms(baseline: dict, current: dict) -> dict:
    shifts = {}
    for bucket in baseline.get("percentages", {}):
        b_pct = baseline["percentages"].get(bucket, 0)
        c_pct = current["percentages"].get(bucket, 0)
        shifts[bucket] = round(c_pct - b_pct, 1)
    regression = any(v < -5 for k, v in shifts.items() if k != "le_inf")
    return {"shifts": shifts, "regression": regression}
