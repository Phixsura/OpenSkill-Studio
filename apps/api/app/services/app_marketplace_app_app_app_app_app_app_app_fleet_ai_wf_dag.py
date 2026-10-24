"""Fleet AI Workflow DAG — track directed acyclic graph task execution."""
from __future__ import annotations
def fleet_ai_workflow_dag(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    dags_24h = sum(e.get("dags_24h", 0) for e in engines)
    nodes_executed = sum(e.get("nodes", 0) for e in engines)
    parallelism = round(sum(e.get("avg_parallelism", 0) for e in engines) / max(len(engines), 1), 1)
    return {"engines": len(engines), "active": len(active), "dags_24h": dags_24h,
            "nodes": nodes_executed, "parallelism": parallelism, "efficient": parallelism > 4}
