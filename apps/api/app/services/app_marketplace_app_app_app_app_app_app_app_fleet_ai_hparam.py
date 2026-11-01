"""Fleet AI Hyperparameter Tuning — track automated hyperparameter optimization."""
from __future__ import annotations
def fleet_ai_hparam_tuning(tuners: list[dict]) -> dict:
    active = [t for t in tuners if t.get("active", True)]
    trials = sum(t.get("trials", 0) for t in tuners)
    best_score = max((t.get("best_score", 0) for t in tuners), default=0)
    search_space = sum(t.get("dimensions", 0) for t in tuners)
    return {"tuners": len(tuners), "active": len(active), "trials": trials,
            "best_score": best_score, "dimensions": search_space, "optimized": trials > 100}
