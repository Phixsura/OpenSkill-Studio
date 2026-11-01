"""Fleet AI Continuous Pretraining — track ongoing foundation model training."""
from __future__ import annotations
def fleet_ai_continuous_pretraining(jobs: list[dict]) -> dict:
    active = [j for j in jobs if j.get("active", True)]
    tokens_total = sum(j.get("tokens_total", 0) for j in jobs)
    loss = round(sum(j.get("loss", 0) for j in jobs) / max(len(jobs), 1), 4)
    gpus = sum(j.get("gpus", 0) for j in jobs)
    return {"jobs": len(jobs), "active": len(active), "tokens_total": tokens_total,
            "loss": loss, "gpus": gpus, "converging": loss < 2.0}
