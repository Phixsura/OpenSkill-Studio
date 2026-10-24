"""Fleet AI Model Parallelism — track tensor and pipeline parallelism."""
from __future__ import annotations
def fleet_ai_model_parallelism(configs: list[dict]) -> dict:
    active = [c for c in configs if c.get("active", True)]
    gpus_used = sum(c.get("gpus", 0) for c in configs)
    tp_degree = max((c.get("tp", 0) for c in configs), default=0)
    pp_degree = max((c.get("pp", 0) for c in configs), default=0)
    efficiency = round(sum(c.get("efficiency_pct", 0) for c in configs) / max(len(configs), 1), 1)
    return {"configs": len(configs), "active": len(active), "gpus": gpus_used,
            "tp": tp_degree, "pp": pp_degree, "efficiency": efficiency, "scalable": efficiency > 80}
