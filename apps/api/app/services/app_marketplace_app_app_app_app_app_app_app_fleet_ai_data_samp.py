"""Fleet AI Data Sampler — track intelligent data sampling strategies."""
from __future__ import annotations
def fleet_ai_data_sampler(samplers: list[dict]) -> dict:
    active = [s for s in samplers if s.get("active", True)]
    sampled_24h = sum(s.get("sampled_24h", 0) for s in samplers)
    strategies = set()
    for s in samplers:
        strategies.update(s.get("strategies", []))
    representativeness = round(sum(s.get("repr_score", 0) for s in samplers) / max(len(samplers), 1), 1)
    return {"samplers": len(samplers), "active": len(active), "sampled_24h": sampled_24h,
            "strategies": len(strategies), "representativeness": representativeness, "balanced": representativeness > 90}
