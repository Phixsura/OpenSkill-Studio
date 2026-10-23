"""GC metrics tracker — monitor garbage collection performance."""
from __future__ import annotations


def analyze_gc(collections: list[dict]) -> dict:
    if not collections:
        return {"total": 0, "avg_pause_ms": 0, "max_pause_ms": 0}
    pauses = [c.get("pause_ms", 0) for c in collections]
    by_gen: dict[str, int] = {}
    for c in collections:
        gen = c.get("generation", "unknown")
        by_gen[gen] = by_gen.get(gen, 0) + 1
    total_pause = sum(pauses)
    return {"total": len(collections), "avg_pause_ms": round(total_pause / len(collections), 2),
            "max_pause_ms": max(pauses), "total_pause_ms": round(total_pause, 2),
            "by_generation": by_gen,
            "gc_pressure": "high" if total_pause > 1000 else "medium" if total_pause > 100 else "low"}


def suggest_tuning(metrics: dict) -> list[dict]:
    suggestions = []
    if metrics.get("gc_pressure") == "high":
        suggestions.append({"action": "increase_heap", "reason": "High GC pressure detected"})
    if metrics.get("max_pause_ms", 0) > 200:
        suggestions.append({"action": "use_concurrent_gc", "reason": f"Long pauses ({metrics['max_pause_ms']}ms)"})
    if metrics.get("by_generation", {}).get("full", 0) > 10:
        suggestions.append({"action": "check_memory_leaks", "reason": "Frequent full GCs"})
    return suggestions
