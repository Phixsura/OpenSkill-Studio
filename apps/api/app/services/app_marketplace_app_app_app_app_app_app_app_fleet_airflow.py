"""Fleet Airflow — track workflow orchestration health."""
from __future__ import annotations
def fleet_airflow_status(environments: list[dict]) -> dict:
    healthy = [e for e in environments if e.get("healthy", True)]
    total_dags = sum(e.get("dags", 0) for e in environments)
    active_runs = sum(e.get("active_runs", 0) for e in environments)
    failed_24h = sum(e.get("failed_24h", 0) for e in environments)
    return {"environments": len(environments), "healthy": len(healthy), "dags": total_dags,
            "active_runs": active_runs, "failed_24h": failed_24h, "reliable": failed_24h == 0}
