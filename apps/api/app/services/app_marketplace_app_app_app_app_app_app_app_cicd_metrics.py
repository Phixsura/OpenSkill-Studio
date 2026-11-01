"""CI/CD pipeline metrics — track build and deploy performance."""
from __future__ import annotations


def analyze_pipelines(runs: list[dict]) -> dict:
    if not runs:
        return {"total_runs": 0}
    passed = sum(1 for r in runs if r.get("status") == "success")
    failed = sum(1 for r in runs if r.get("status") == "failed")
    durations = [r.get("duration_sec", 0) for r in runs]
    avg_duration = round(sum(durations) / len(durations))
    p95_duration = sorted(durations)[int(len(durations) * 0.95)]
    return {"total_runs": len(runs), "passed": passed, "failed": failed,
            "pass_rate": round(passed / len(runs) * 100),
            "avg_duration_sec": avg_duration, "p95_duration_sec": p95_duration,
            "fastest_sec": min(durations), "slowest_sec": max(durations)}


def deployment_frequency(deploys: list[dict], period_days: int = 30) -> dict:
    total = len(deploys)
    per_day = round(total / max(period_days, 1), 1)
    per_week = round(per_day * 7, 1)
    level = "elite" if per_day >= 1 else "high" if per_week >= 1 else "medium" if total >= 4 else "low"
    return {"total_deploys": total, "per_day": per_day, "per_week": per_week,
            "period_days": period_days, "dora_level": level}
