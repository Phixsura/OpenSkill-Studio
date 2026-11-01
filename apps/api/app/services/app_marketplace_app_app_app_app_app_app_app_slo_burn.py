"""SLO burn rate calculator — calculate error budget burn rate."""
from __future__ import annotations


def calculate_burn_rate(total_requests: int, failed_requests: int,
                        slo_target: float, window_hours: int) -> dict:
    error_rate = failed_requests / max(total_requests, 1)
    budget = 1.0 - slo_target
    burn_rate = round(error_rate / max(budget, 0.0001), 2)
    budget_consumed_pct = round(burn_rate * window_hours / 720 * 100, 2)  # 30-day window
    exhaustion_hours = round(720 / max(burn_rate, 0.01), 1) if burn_rate > 0 else float("inf")
    severity = "critical" if burn_rate > 10 else ("warning" if burn_rate > 2 else "ok")
    return {"burn_rate": burn_rate, "error_rate": round(error_rate, 6),
            "budget": round(budget, 6), "budget_consumed_pct": budget_consumed_pct,
            "exhaustion_hours": exhaustion_hours, "severity": severity,
            "window_hours": window_hours}


def multi_window(windows: list[dict], slo_target: float) -> dict:
    results = []
    for w in windows:
        r = calculate_burn_rate(w["total"], w["failed"], slo_target, w["hours"])
        results.append({"window": f"{w['hours']}h", **r})
    alerting = any(r["severity"] != "ok" for r in results)
    return {"windows": results, "slo_target": slo_target, "alerting": alerting}
