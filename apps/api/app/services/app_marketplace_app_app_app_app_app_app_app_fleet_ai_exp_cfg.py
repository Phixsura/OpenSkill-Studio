"""Fleet AI Experiment Config — track ML experiment configuration management."""
from __future__ import annotations
def fleet_ai_experiment_config(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    configs = sum(m.get("configs", 0) for m in managers)
    templates = sum(m.get("templates", 0) for m in managers)
    overrides_24h = sum(m.get("overrides_24h", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "configs": configs,
            "templates": templates, "overrides_24h": overrides_24h, "organized": templates > 10}
