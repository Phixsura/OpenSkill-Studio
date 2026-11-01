"""Fleet AI Eval Dataset — track curated evaluation dataset management."""
from __future__ import annotations
def fleet_ai_eval_dataset(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    datasets = sum(m.get("datasets", 0) for m in managers)
    samples = sum(m.get("samples", 0) for m in managers)
    domains = sum(m.get("domains", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "datasets": datasets,
            "samples": samples, "domains": domains, "comprehensive": domains > 10}
