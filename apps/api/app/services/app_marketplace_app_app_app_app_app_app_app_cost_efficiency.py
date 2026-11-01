"""Cost efficiency scorer — score infrastructure cost efficiency."""
from __future__ import annotations


def score_efficiency(resources: list[dict]) -> dict:
    total_cost = sum(r.get("cost", 0) for r in resources)
    total_util = 0
    count = 0
    wasteful = []
    for r in resources:
        util = r.get("utilization_pct", 0)
        total_util += util
        count += 1
        if util < 20:
            wasteful.append({"name": r["name"], "cost": r["cost"],
                              "utilization": util, "potential_savings": round(r["cost"] * 0.6, 2)})
    avg_util = round(total_util / max(count, 1), 1)
    total_waste = sum(w["potential_savings"] for w in wasteful)
    score = round(avg_util * 0.7 + min(100, (1 - len(wasteful) / max(count, 1)) * 100) * 0.3, 1)
    return {"score": score, "avg_utilization": avg_util,
            "total_cost": round(total_cost, 2), "potential_savings": round(total_waste, 2),
            "wasteful_resources": sorted(wasteful, key=lambda w: -w["potential_savings"]),
            "resources_analyzed": count}
