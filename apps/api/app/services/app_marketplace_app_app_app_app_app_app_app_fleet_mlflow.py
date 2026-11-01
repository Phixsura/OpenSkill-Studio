"""Fleet MLflow — track ML lifecycle management."""
from __future__ import annotations
def fleet_mlflow_status(servers: list[dict]) -> dict:
    running = [s for s in servers if s.get("running", True)]
    experiments = sum(s.get("experiments", 0) for s in servers)
    runs = sum(s.get("runs_24h", 0) for s in servers)
    models_registered = sum(s.get("registered_models", 0) for s in servers)
    return {"servers": len(servers), "running": len(running), "experiments": experiments,
            "runs_24h": runs, "registered_models": models_registered}
