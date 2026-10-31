"""Fleet AI LoRA Adapter — track low-rank adaptation for model fine-tuning."""
from __future__ import annotations
def fleet_ai_lora(adapters: list[dict]) -> dict:
    active = [a for a in adapters if a.get("active", True)]
    rank = max((a.get("rank", 0) for a in adapters), default=0)
    adapters_trained = sum(a.get("trained", 0) for a in adapters)
    param_pct = round(sum(a.get("param_pct", 0) for a in adapters) / max(len(adapters), 1), 2)
    return {"adapters": len(adapters), "active": len(active), "rank": rank,
            "trained": adapters_trained, "param_pct": param_pct, "efficient": param_pct < 1}
