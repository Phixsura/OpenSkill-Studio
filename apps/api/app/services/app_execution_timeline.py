"""Execution timeline — build time-series for execution metrics."""

from collections import defaultdict


def build_execution_timeline(executions: list[dict], *, group_by: str = "hour") -> list[dict]:
    groups: dict[str, dict] = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0, "total_ms": 0})
    for ex in executions:
        ts = ex.get("created_at", "")[:13] if group_by == "hour" else ex.get("created_at", "")[:10]
        groups[ts]["total"] += 1
        groups[ts]["total_ms"] += ex.get("duration_ms", 0)
        if ex.get("success", True):
            groups[ts]["success"] += 1
        else:
            groups[ts]["failed"] += 1
    return [{"period": k, **v, "avg_ms": round(v["total_ms"] / v["total"], 1) if v["total"] else 0}
            for k, v in sorted(groups.items())]
