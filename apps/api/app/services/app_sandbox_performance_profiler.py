"""Sandbox performance profiler — profile execution performance patterns."""

from collections import defaultdict


def profile_executions(executions: list[dict]) -> dict:
    """Profile execution performance by function."""
    funcs: dict[str, list[int]] = defaultdict(list)
    for ex in executions:
        funcs[ex.get("function_name", "unknown")].append(ex.get("duration_ms", 0))
    
    profiles = {}
    for fn, durations in funcs.items():
        s = sorted(durations)
        n = len(s)
        profiles[fn] = {
            "count": n, "min_ms": s[0], "max_ms": s[-1],
            "avg_ms": round(sum(s) / n, 1),
            "p50_ms": s[n // 2], "p95_ms": s[int(n * 0.95)],
            "total_ms": sum(s),
        }
    return profiles


def find_bottlenecks(profiles: dict, *, threshold_ms: int = 500) -> list[dict]:
    return [{"function": fn, **stats} for fn, stats in profiles.items() if stats["p95_ms"] > threshold_ms]
