"""Fleet Hopsworks — track ML feature platform."""
from __future__ import annotations
def fleet_hopsworks_status(clusters: list[dict]) -> dict:
    running = [c for c in clusters if c.get("running", True)]
    feature_groups = sum(c.get("feature_groups", 0) for c in clusters)
    models = sum(c.get("models", 0) for c in clusters)
    return {"clusters": len(clusters), "running": len(running), "feature_groups": feature_groups,
            "models": models, "all_running": len(running) == len(clusters)}
