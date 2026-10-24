"""Runtime performance profiler — real-time performance analysis."""
from __future__ import annotations


def profile_runtime(metrics: dict) -> dict:
    gc_pause = metrics.get("gc_pause_ms", 0)
    heap_used = metrics.get("heap_used_mb", 0)
    heap_total = metrics.get("heap_total_mb", 1)
    event_loop_lag = metrics.get("event_loop_lag_ms", 0)
    active_handles = metrics.get("active_handles", 0)
    
    heap_pct = round(heap_used / max(heap_total, 1) * 100, 1)
    issues = []
    if gc_pause > 100:
        issues.append(f"High GC pause: {gc_pause}ms")
    if heap_pct > 85:
        issues.append(f"Memory pressure: {heap_pct}%")
    if event_loop_lag > 50:
        issues.append(f"Event loop lag: {event_loop_lag}ms")
    
    health = "healthy" if not issues else "degraded" if len(issues) < 2 else "critical"
    return {"gc_pause_ms": gc_pause, "heap_pct": heap_pct,
            "event_loop_lag_ms": event_loop_lag, "active_handles": active_handles,
            "issues": issues, "health": health}
