"""Resource cost tag — tag resources with cost allocation metadata."""
from __future__ import annotations


def tag_cost(resources: list[dict]) -> dict:
    by_tag: dict[str, float] = {}
    untagged_cost = 0
    for r in resources:
        cost = r.get("cost", 0)
        tags = r.get("tags", {})
        cost_center = tags.get("cost_center", "")
        if cost_center:
            by_tag[cost_center] = round(by_tag.get(cost_center, 0) + cost, 2)
        else:
            untagged_cost += cost
    total = round(sum(by_tag.values()) + untagged_cost, 2)
    return {"by_cost_center": by_tag, "untagged_cost": round(untagged_cost, 2),
            "total_cost": total, "tagged_pct": round((total - untagged_cost) / max(total, 0.01) * 100),
            "cost_centers": sorted(by_tag.keys())}
