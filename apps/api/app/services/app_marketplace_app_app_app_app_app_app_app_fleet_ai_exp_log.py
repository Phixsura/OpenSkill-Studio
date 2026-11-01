"""Fleet AI Experiment Log — track ML experiment run logging."""
from __future__ import annotations
def fleet_ai_experiment_log(loggers: list[dict]) -> dict:
    active = [l for l in loggers if l.get("active", True)]
    experiments = sum(l.get("experiments", 0) for l in loggers)
    runs = sum(l.get("runs", 0) for l in loggers)
    artifacts = sum(l.get("artifacts", 0) for l in loggers)
    return {"loggers": len(loggers), "active": len(active), "experiments": experiments,
            "runs": runs, "artifacts": artifacts, "logging": experiments > 0}
