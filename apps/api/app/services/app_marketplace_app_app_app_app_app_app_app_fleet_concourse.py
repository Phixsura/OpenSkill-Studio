"""Fleet Concourse CI — track resource and job health."""
from __future__ import annotations
def fleet_concourse_status(pipelines: list[dict]) -> dict:
    paused = [p for p in pipelines if p.get("paused", False)]
    jobs_ok = sum(p.get("jobs_passing", 0) for p in pipelines)
    jobs_fail = sum(p.get("jobs_failing", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "paused": len(paused), "jobs_passing": jobs_ok,
            "jobs_failing": jobs_fail, "healthy": jobs_fail == 0}
