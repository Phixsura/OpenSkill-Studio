"""Fleet AI Experiment Versioning — track ML experiment reproducibility."""
from __future__ import annotations
def fleet_ai_experiment_versioning(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    experiments = sum(s.get("experiments", 0) for s in systems)
    snapshots = sum(s.get("snapshots", 0) for s in systems)
    reproducible_pct = round(sum(s.get("reproducible_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "experiments": experiments,
            "snapshots": snapshots, "reproducible_pct": reproducible_pct, "reproducible": reproducible_pct > 95}
