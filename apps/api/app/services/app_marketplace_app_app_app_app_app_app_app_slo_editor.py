"""SLO editor — create and manage service level objectives."""
from __future__ import annotations


def create_slo(name: str, metric: str, target: float, window_days: int = 30,
                alert_burn_rate: float = 6.0) -> dict:
    error_budget_pct = round(100 - target, 3)
    return {"name": name, "metric": metric, "target_pct": target,
            "error_budget_pct": error_budget_pct, "window_days": window_days,
            "alert_burn_rate": alert_burn_rate}


def validate_slo(slo: dict) -> dict:
    issues = []
    if slo["target_pct"] < 90:
        issues.append("Target below 90% — unusually low")
    if slo["target_pct"] > 99.999:
        issues.append("Target above 99.999% — unrealistic")
    if slo["window_days"] < 7:
        issues.append("Window too short — minimum 7 days recommended")
    return {"valid": len(issues) == 0, "issues": issues, "issue_count": len(issues)}


def slo_catalog(slos: list[dict]) -> dict:
    by_metric: dict[str, int] = {}
    for s in slos:
        by_metric[s["metric"]] = by_metric.get(s["metric"], 0) + 1
    avg_target = round(sum(s["target_pct"] for s in slos) / max(len(slos), 1), 2)
    return {"total": len(slos), "by_metric": by_metric, "avg_target": avg_target}
