"""Fleet innovation index — measure platform innovation velocity."""
from __future__ import annotations
def fleet_innovation_index(metrics: dict) -> dict:
    new_features = metrics.get("new_features_30d", 0)
    experiments = metrics.get("experiments_30d", 0)
    adoption_rate = metrics.get("feature_adoption_pct", 0)
    index = round((new_features * 2 + experiments + adoption_rate) / 4, 1)
    return {"new_features": new_features, "experiments": experiments,
            "adoption_rate": adoption_rate, "index": index,
            "innovative": index > 50}
