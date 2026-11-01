"""Performance profiler — profile and identify bottlenecks."""
from __future__ import annotations


def profile_request(spans: list[dict]) -> dict:
    total_ms = sum(s.get("duration_ms", 0) for s in spans)
    sorted_spans = sorted(spans, key=lambda s: -s.get("duration_ms", 0))
    bottleneck = sorted_spans[0] if sorted_spans else None
    self_times = []
    for s in spans:
        child_time = sum(c.get("duration_ms", 0) for c in spans if c.get("parent") == s.get("name"))
        self_time = s.get("duration_ms", 0) - child_time
        self_times.append({**s, "self_ms": round(self_time, 2),
                           "pct": round(self_time / max(total_ms, 0.01) * 100, 1)})
    return {"total_ms": total_ms, "span_count": len(spans),
            "bottleneck": bottleneck["name"] if bottleneck else None,
            "self_times": sorted(self_times, key=lambda s: -s["self_ms"]),
            "optimization_target": self_times[0]["name"] if self_times else None}


def compare_profiles(before: dict, after: dict) -> dict:
    delta = round(after["total_ms"] - before["total_ms"], 2)
    improvement = round(-delta / max(before["total_ms"], 0.01) * 100, 1)
    return {"before_ms": before["total_ms"], "after_ms": after["total_ms"],
            "delta_ms": delta, "improvement_pct": improvement,
            "improved": delta < 0}
