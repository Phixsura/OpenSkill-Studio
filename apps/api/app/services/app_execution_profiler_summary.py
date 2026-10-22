"""Execution profiler summary — compile profiling data for developer dashboard."""


def build_profiler_summary(executions: list[dict]) -> dict:
    if not executions:
        return {"total": 0, "avg_ms": 0, "p95_ms": 0, "slowest_function": None, "fastest_function": None}
    
    by_fn: dict[str, list[int]] = {}
    for ex in executions:
        fn = ex.get("function_name", "unknown")
        if fn not in by_fn: by_fn[fn] = []
        by_fn[fn].append(ex.get("duration_ms", 0))
    
    all_durations = sorted(d for ex in executions for d in [ex.get("duration_ms", 0)])
    fn_avgs = {fn: round(sum(ds) / len(ds), 1) for fn, ds in by_fn.items()}
    
    return {
        "total": len(executions),
        "avg_ms": round(sum(all_durations) / len(all_durations), 1),
        "p95_ms": all_durations[int(len(all_durations) * 0.95)] if all_durations else 0,
        "slowest_function": max(fn_avgs, key=fn_avgs.get) if fn_avgs else None,
        "fastest_function": min(fn_avgs, key=fn_avgs.get) if fn_avgs else None,
        "function_count": len(by_fn),
        "by_function": fn_avgs,
    }
