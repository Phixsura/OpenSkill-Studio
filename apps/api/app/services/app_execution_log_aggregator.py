"""Execution log aggregator — summarize execution patterns."""

from collections import defaultdict


def aggregate_by_function(executions: list[dict]) -> list[dict]:
    """Aggregate execution stats by function name."""
    funcs: dict[str, dict] = defaultdict(lambda: {"count": 0, "success": 0, "total_ms": 0, "errors": []})
    for ex in executions:
        fn = ex.get("function_name", "unknown")
        funcs[fn]["count"] += 1
        funcs[fn]["total_ms"] += ex.get("duration_ms", 0)
        if ex.get("success", True):
            funcs[fn]["success"] += 1
        elif ex.get("error"):
            funcs[fn]["errors"].append(ex["error"])
    
    return [{"function": fn, "count": s["count"], "success_rate": round(s["success"] / s["count"] * 100, 1),
             "avg_ms": round(s["total_ms"] / s["count"], 1), "unique_errors": len(set(s["errors"]))}
            for fn, s in sorted(funcs.items(), key=lambda x: x[1]["count"], reverse=True)]


def find_slow_functions(executions: list[dict], *, threshold_ms: int = 1000) -> list[dict]:
    """Find functions that frequently exceed the threshold."""
    return [e for e in executions if e.get("duration_ms", 0) > threshold_ms]
