"""Fleet CI Analytics v9 — track CI pipeline performance and flake rates."""
from __future__ import annotations
def fleet_ci_analytics_v9(pipelines: list[dict]) -> dict:
    total_runs = sum(p.get("runs_today", 0) for p in pipelines)
    success_rate = sum(p.get("success_rate", 0) for p in pipelines) / len(pipelines) if pipelines else 0
    avg_duration = sum(p.get("avg_duration_sec", 0) for p in pipelines) / len(pipelines) if pipelines else 0
    flaky = sum(p.get("flaky_tests", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "runs_today": total_runs, "avg_success_rate": round(success_rate, 1),
            "avg_duration_sec": round(avg_duration, 1), "flaky_tests": flaky, "healthy": success_rate > 95}
