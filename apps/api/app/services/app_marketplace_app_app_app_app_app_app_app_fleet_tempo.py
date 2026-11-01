"""Fleet Tempo — track Grafana Tempo trace storage."""
from __future__ import annotations
def fleet_tempo_status(instances: list[dict]) -> dict:
    healthy = [i for i in instances if i.get("healthy", True)]
    traces_per_sec = sum(i.get("traces_per_sec", 0) for i in instances)
    retention_days = min((i.get("retention_days", 30) for i in instances), default=30)
    return {"instances": len(instances), "healthy": len(healthy), "traces_per_sec": traces_per_sec,
            "min_retention_days": retention_days, "all_healthy": len(healthy) == len(instances)}
