"""API response time SLA — track response time against SLA targets."""
from __future__ import annotations


def check_response_time_sla(endpoints: list[dict]) -> dict:
    results = []
    met = 0
    for ep in endpoints:
        p99 = ep.get("p99_ms", 0)
        target = ep.get("target_ms", 500)
        within = p99 <= target
        if within:
            met += 1
        margin = round(target - p99, 1)
        results.append({"endpoint": ep.get("path", ""), "p99_ms": p99,
                         "target_ms": target, "within_sla": within, "margin_ms": margin})
    total = len(results)
    return {"results": results, "total": total, "met": met,
            "breached": total - met, "sla_pct": round(met / max(total, 1) * 100)}


def response_time_trend(history: list[float]) -> dict:
    if len(history) < 2:
        return {"trend": "insufficient"}
    delta = round(history[-1] - history[0], 1)
    avg = round(sum(history) / len(history), 1)
    return {"latest": history[-1], "avg": avg, "delta": delta,
            "improving": delta < 0, "stable": abs(delta) < 10}
