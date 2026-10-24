"""Mesh outlier detection — detect outlier instances in the service mesh."""
from __future__ import annotations
import math


def detect_outliers(instances: list[dict], threshold_std: float = 2.0) -> dict:
    if len(instances) < 3:
        return {"outliers": [], "total": len(instances)}
    error_rates = [i.get("error_rate_pct", 0) for i in instances]
    mean = sum(error_rates) / len(error_rates)
    std = math.sqrt(sum((x - mean) ** 2 for x in error_rates) / len(error_rates))
    outliers = []
    for inst in instances:
        er = inst.get("error_rate_pct", 0)
        z = (er - mean) / max(std, 0.001)
        if z > threshold_std:
            outliers.append({"instance": inst["id"], "error_rate": er,
                              "z_score": round(z, 2), "action": "eject"})
    return {"outliers": outliers, "total": len(instances), "mean_error": round(mean, 2),
            "std": round(std, 2), "ejections_needed": len(outliers)}
