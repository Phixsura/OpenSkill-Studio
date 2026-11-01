"""Fleet Buildkite — track build agent and pipeline metrics."""
from __future__ import annotations
def fleet_buildkite_status(pipelines: list[dict]) -> dict:
    passing = [p for p in pipelines if p.get("passing", True)]
    total_agents = sum(p.get("agents", 0) for p in pipelines)
    queue_time = round(sum(p.get("avg_queue_sec", 0) for p in pipelines) / max(len(pipelines), 1), 1)
    return {"pipelines": len(pipelines), "passing": len(passing), "agents": total_agents,
            "avg_queue_sec": queue_time, "fast_queue": queue_time < 30}
